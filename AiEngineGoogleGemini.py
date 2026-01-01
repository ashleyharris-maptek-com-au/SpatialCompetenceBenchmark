"""
Google Gemini AI Engine for MeshBenchmark

This module provides an interface to the Google Gemini API using the latest google-genai SDK.

Setup:
1. Install the SDK: pip install google-genai
2. Set your API key as an environment variable:
   - Windows: set GEMINI_API_KEY=your_api_key_here
   - Linux/Mac: export GEMINI_API_KEY=your_api_key_here
   
Get your API key from: https://ai.google.dev/

The SDK documentation can be found at: https://googleapis.github.io/python-genai/
"""

import hashlib
import os
import json
import PromptImageTagging as pit
import time
import threading
import queue
from urllib.request import Request, urlopen
from typing import Any, List, Optional
from google import genai
from google.genai import types
from pydantic import BaseModel, create_model

TIMEOUT_SECONDS = 3600  # 1 hour timeout


class GeminiEngine:
  """
  Google Gemini AI Engine class.
  
  Configuration parameters:
  - model: Model name (e.g., "gemini-2.5-flash")
  - reasoning: Reasoning effort on a 0-10 scale:
      - 0 or False: Thinking disabled (fastest, no reasoning)
      - 1-3: Low reasoning (maps to ~128-1024 token budget)
      - 4-7: Medium reasoning (maps to ~2048-8192 token budget)
      - 8-10: High reasoning (maps to ~12288-24576 token budget)
  - tools: Tool capabilities:
      - False: No tools available
      - "google_search": Enable Google Search grounding
      - "code_execution": Enable Python code execution
      - List of functions: Enable custom function calling
      - List of strings/functions: Mix built-in and custom tools
  """

  def __init__(self, model: str, reasoning=False, tools=False):
    self.model = model
    self.reasoning = reasoning
    self.tools = tools
    self.configAndSettingsHash = hashlib.sha256(model.encode() + str(reasoning).encode() +
                                                str(tools).encode()).hexdigest()

  def AIHook(self, prompt: str, structure: dict | None) -> tuple:
    """Call the Gemini API with instance configuration."""
    return _gemini_ai_hook(prompt, structure, self.model, self.reasoning, self.tools)


def json_schema_to_pydantic(schema: dict, name: str = "DynamicModel") -> type[BaseModel]:
  """
    Convert a JSON schema dict to a Pydantic model class.
    Supports basic types: string, number, integer, boolean, array, object.
    """

  def get_python_type(prop_schema: dict) -> Any:
    """Convert JSON schema type to Python/Pydantic type."""
    json_type = prop_schema.get("type", "string")

    if json_type == "string":
      return str
    elif json_type == "number":
      return float
    elif json_type == "integer":
      return int
    elif json_type == "boolean":
      return bool
    elif json_type == "array":
      items_schema = prop_schema.get("items", {})
      item_type = get_python_type(items_schema)
      return List[item_type]
    elif json_type == "object":
      # Nested object - create a nested model
      nested_props = prop_schema.get("properties", {})
      if nested_props:
        return json_schema_to_pydantic(prop_schema, name + "Nested")
      return dict
    else:
      return Any

  properties = schema.get("properties", {})
  required = set(schema.get("required", []))

  # Build field definitions for create_model
  field_definitions = {}
  for prop_name, prop_schema in properties.items():
    python_type = get_python_type(prop_schema)
    if prop_name in required:
      field_definitions[prop_name] = (python_type, ...)
    else:
      field_definitions[prop_name] = (Optional[python_type], None)

  return create_model(name, **field_definitions)


def _build_gemini_contents(prompt: str, structure: dict | None, tools) -> list[Any]:
  prompt_parts = pit.parse_prompt_parts(prompt)
  contents: list[Any] = []
  for part_type, part_value in prompt_parts:
    if part_type == "text":
      if part_value:
        contents.append(part_value)
    elif part_type == "image":
      if pit.is_url(part_value):
        req = Request(part_value, headers={"User-Agent": "MeshBenchmark/1.0"})
        with urlopen(req, timeout=30) as resp:
          content_type = resp.headers.get("Content-Type")
          image_bytes = resp.read()

        mime_type = None
        if content_type:
          mime_type = content_type.split(";", 1)[0].strip().lower()
        if not mime_type:
          mime_type = pit.guess_image_mime_type_from_ref(part_value)

        contents.append(types.Part.from_bytes(data=image_bytes, mime_type=mime_type))
      elif pit.is_data_uri(part_value):
        mime_type, image_bytes = pit.decode_data_uri(part_value)
        contents.append(types.Part.from_bytes(data=image_bytes, mime_type=mime_type))
      else:
        local_path = pit.resolve_local_path(part_value)
        mime_type = pit.guess_image_mime_type_from_path(local_path)
        image_bytes = pit.read_file_bytes(local_path)
        contents.append(types.Part.from_bytes(data=image_bytes, mime_type=mime_type))

  if structure is not None and tools:
    schema_json = json.dumps(structure, indent=2)
    contents.append(f"""

You MUST respond with valid JSON that matches this exact schema:
{schema_json}

Return ONLY the JSON object, no markdown formatting, no code blocks, no explanation.""")

  if not contents:
    contents = [""]

  return contents


def _gemini_ai_hook(prompt: str, structure: dict | None, model: str, reasoning,
                    tools) -> dict | str:
  """
    This function is called by the test runner to get the AI's response to a prompt.
    
    Prompt is the question to ask the AI.
    Structure contains the JSON schema for the expected output. If it is None, the output is just a string.
    
    There is no memory between calls to this function, the 'conversation' doesn't persist.
    
    Returns tuple of (result, chainOfThought).
    """
  # Initialize the client - it will automatically use the GEMINI_API_KEY or GOOGLE_API_KEY
  # environment variable
  client = genai.Client()

  try:
    # Build configuration based on constants
    config_params = {}

    # Add structured output if schema provided (but not when tools are enabled - Gemini doesn't support both)
    if structure is not None and not tools:

      # For some studpid reason, OpenAI REQUIRE that you specify AdditionalProperties=False
      # in the schema, whereas Gemini seems to fail if it's even mentioned.... grr.
      # Remove "AdditionalProperties" recursively
      def remove_additional_properties(schema):
        if isinstance(schema, dict):
          # Remove AdditionalProperties key
          schema.pop("additionalProperties", None)
          # Recursively process all values
          for key, value in schema.items():
            if isinstance(value, dict):
              remove_additional_properties(value)
            elif isinstance(value, list) and value and isinstance(value[0], dict):
              for item in value:
                if isinstance(item, dict):
                  remove_additional_properties(item)
        return schema

      cleaned_structure = remove_additional_properties(structure.copy())

      config_params['response_mime_type'] = 'application/json'
      config_params['response_schema'] = cleaned_structure

    # Add thinking/reasoning configuration if reasoning is set
    # Map 0-10 scale to Gemini's thinking_budget (0-24576)
    if reasoning and reasoning != 0:
      # Map 1-10 to appropriate token budgets
      if isinstance(reasoning, int) and reasoning > 0:
        if reasoning <= 3:
          thinking_budget = 128 * (2**(reasoning - 1))  # 128, 256, 512
        elif reasoning <= 7:
          thinking_budget = 1024 * (2**(reasoning - 4))  # 1024, 2048, 4096, 8192
        else:
          thinking_budget = 8192 * (2**(reasoning - 7))  # 8192, 16384, 24576 (capped)
        thinking_budget = min(thinking_budget, 24576)  # Cap at max
      else:
        thinking_budget = 1024  # Default for truthy non-int values

      config_params['thinking_config'] = types.ThinkingConfig(thinking_budget=thinking_budget)

    # Add tools if specified (supports built-in and custom tools)
    if tools and tools is not False:
      tools_list = []

      # Handle single tool or list of tools
      tools_to_process = tools if isinstance(tools, list) else [tools]

      for tool in tools_to_process:
        if isinstance(tool, str):
          # Built-in tool specified by name
          if tool == "google_search":
            tools_list.append(types.Tool(google_search=types.GoogleSearch()))
          elif tool == "code_execution":
            tools_list.append(types.Tool(code_execution=types.ToolCodeExecution()))
          else:
            print(f"Warning: Unknown built-in tool '{tool}', ignoring")
        elif tool is True:
          # tools=True means "enable tools" but no specific tool specified
          tools_list.append(types.Tool(code_execution=types.ToolCodeExecution()))
          tools_list.append(types.Tool(google_search=types.GoogleSearch()))
        elif callable(tool):
          # Custom function - pass directly (SDK handles it)
          tools_list.append(tool)
        else:
          print(f"Warning: Invalid tool type {type(tool)}, ignoring")

      if tools_list:
        config_params['tools'] = tools_list

    # Create config object
    config = types.GenerateContentConfig(**config_params) if config_params else None

    prompt_parts = pit.parse_prompt_parts(prompt)
    contents: list[Any] = []
    for part_type, part_value in prompt_parts:
      if part_type == "text":
        if part_value:
          contents.append(part_value)
      elif part_type == "image":
        if pit.is_url(part_value):
          req = Request(part_value, headers={"User-Agent": "MeshBenchmark/1.0"})
          with urlopen(req, timeout=30) as resp:
            content_type = resp.headers.get("Content-Type")
            image_bytes = resp.read()

          mime_type = None
          if content_type:
            mime_type = content_type.split(";", 1)[0].strip().lower()
          if not mime_type:
            mime_type = pit.guess_image_mime_type_from_ref(part_value)

          contents.append(types.Part.from_bytes(data=image_bytes, mime_type=mime_type))
        elif pit.is_data_uri(part_value):
          mime_type, image_bytes = pit.decode_data_uri(part_value)
          contents.append(types.Part.from_bytes(data=image_bytes, mime_type=mime_type))
        else:
          local_path = pit.resolve_local_path(part_value)
          mime_type = pit.guess_image_mime_type_from_path(local_path)
          image_bytes = pit.read_file_bytes(local_path)
          contents.append(types.Part.from_bytes(data=image_bytes, mime_type=mime_type))

    if structure is not None and tools:
      schema_json = json.dumps(structure, indent=2)
      contents.append(f"""

You MUST respond with valid JSON that matches this exact schema:
{schema_json}

Return ONLY the JSON object, no markdown formatting, no code blocks, no explanation.""")

    if not contents:
      contents = [""]

    # Generate content with streaming to capture thinking in real-time
    chainOfThought = ""
    output_text = ""
    current_thinking_line = ""

    stream = client.models.generate_content_stream(model=model, contents=contents, config=config)

    # Use a thread + queue to enable hard timeout on frozen streams
    chunk_queue = queue.Queue()

    def stream_reader():
      """Read chunks from stream and put them in queue."""
      try:
        for chunk in stream:
          chunk_queue.put(("chunk", chunk))
        chunk_queue.put(("done", None))
      except Exception as e:
        chunk_queue.put(("error", e))

    reader_thread = threading.Thread(target=stream_reader, daemon=True)
    reader_thread.start()

    start_time = time.time()
    timed_out = False

    while True:
      # Check total elapsed time
      elapsed = time.time() - start_time
      if elapsed > TIMEOUT_SECONDS:
        print(f"Timeout: Gemini API call exceeded {TIMEOUT_SECONDS} seconds")
        timed_out = True
        break

      # Wait for next chunk with timeout (check every 30 seconds)
      remaining = TIMEOUT_SECONDS - elapsed
      try:
        msg_type, payload = chunk_queue.get(timeout=min(30, remaining))
      except queue.Empty:
        continue  # No chunk yet, loop back to check timeout

      if msg_type == "done":
        break
      elif msg_type == "error":
        print(f"Stream error: {payload}")
        break
      elif msg_type == "chunk":
        chunk = payload
        # Process each candidate in the chunk
        for candidate in chunk.candidates:
          if candidate.content and candidate.content.parts:
            for part in candidate.content.parts:
              # Check if this is a thinking part
              if hasattr(part, 'thought') and part.thought:
                # This is thinking content
                thought_text = part.text if hasattr(part, 'text') else ""
                current_thinking_line += thought_text
                # Print complete lines as they arrive
                while "\n" in current_thinking_line:
                  line, current_thinking_line = current_thinking_line.split("\n", 1)
                  print(f"Thinking: {line}", flush=True)
                  chainOfThought += line + "\n"
              elif hasattr(part, 'text') and part.text:
                # This is regular output content
                output_text += part.text

    # Flush any remaining thinking content
    if current_thinking_line:
      print(f"Thinking: {current_thinking_line}", flush=True)
      chainOfThought += current_thinking_line

    # Strip trailing newline from chain of thought
    chainOfThought = chainOfThought.rstrip("\n")

    if chainOfThought:
      print()  # Blank line after thinking

    # Parse and return response
    if structure is not None:
      if output_text:
        # Try to extract JSON from output (model may wrap it in markdown)
        json_text = output_text.strip()
        if json_text.startswith("```json"):
          json_text = json_text[7:]
        if json_text.startswith("```"):
          json_text = json_text[3:]
        if json_text.endswith("```"):
          json_text = json_text[:-3]
        json_text = json_text.strip()

        try:
          # When tools are enabled, use Pydantic for full schema validation
          if tools and structure:
            try:
              pydantic_model = json_schema_to_pydantic(structure, "ResponseModel")
              parsed_obj = pydantic_model.model_validate_json(json_text)
              return parsed_obj.model_dump(), chainOfThought
            except Exception as e:
              return {}, chainOfThought
          else:
            parsed = json.loads(json_text)
            return parsed, chainOfThought
        except json.JSONDecodeError as e:
          print(f"Warning: Failed to parse JSON response: {e}")
          print(f"Raw output was: {output_text[:500]}")
          return {}, chainOfThought
      return {}, chainOfThought
    else:
      return output_text or "", chainOfThought

  except Exception as e:
    print(f"Error calling Gemini API: {e}")

    # Check for content policy violation
    from ContentViolationHandler import is_content_violation_gemini
    if is_content_violation_gemini(error=e):
      print("CONTENT VIOLATION DETECTED (Gemini)")
      if structure is not None:
        return {"__content_violation__": True, "reason": str(e)}, f"Content violation: {e}"
      else:
        return "__content_violation__", f"Content violation: {e}"

    # Return appropriate empty response based on structure
    if structure is not None:
      return {}, ""
    else:
      return "", ""
