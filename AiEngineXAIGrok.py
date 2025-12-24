"""
xAI Grok AI Engine for MeshBenchmark

This module provides an interface to the xAI Grok API using the official xai-sdk.

Setup:
1. Install the SDK: pip install xai-sdk
2. Set your API key as an environment variable:
   - Windows: set XAI_API_KEY=your_api_key_here
   - Linux/Mac: export XAI_API_KEY=your_api_key_here
   
Get your API key from: https://console.x.ai/

The SDK documentation can be found at: https://docs.x.ai/
"""

import hashlib

# Constants that fine tune which model, whether reasoning is used and how much, and whether tools
# are made available.
MODEL = "grok-3-mini"

# REASONING controls reasoning effort on a 0-10 scale:
# - 0 or False: No reasoning (fastest)
# - 1-3: Low reasoning effort
# - 4-7: Medium reasoning effort
# - 8-10: High reasoning effort
REASONING = False

# TOOLS enables tool capabilities:
# - False: No tools available
# - True: Enable built-in tools (web_search, x_search, code_execution)
# - List of function definitions: Enable specific custom tools
#
# Examples:
#   TOOLS = False                    # No tools
#   TOOLS = True                     # All built-in tools
#   TOOLS = ["web_search"]           # Just web search
#   TOOLS = [function_def]           # Custom function only
TOOLS = False

configAndSettingsHash = hashlib.sha256(MODEL.encode() + str(REASONING).encode() +
                                       str(TOOLS).encode() + b"version2").hexdigest()


def Configure(Model, Reasoning, Tools):
  global MODEL
  global REASONING
  global TOOLS
  global configAndSettingsHash
  MODEL = Model
  REASONING = Reasoning
  TOOLS = Tools
  configAndSettingsHash = hashlib.sha256(MODEL.encode() + str(REASONING).encode() +
                                         str(TOOLS).encode() + b"version2").hexdigest()


import os
import json
import PromptImageTagging as pit
from typing import Any, List, Optional
from pydantic import BaseModel, create_model


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


def build_xai_user_args(prompt: str, structure: dict | None) -> list[Any]:
  from xai_sdk.chat import image

  prompt_parts = pit.parse_prompt_parts(prompt)
  user_args: list[Any] = []
  for part_type, part_value in prompt_parts:
    if part_type == "text":
      if part_value:
        user_args.append(part_value)
    elif part_type == "image":
      if pit.is_url(part_value):
        user_args.append(image(part_value))
      elif pit.is_data_uri(part_value):
        _, b64 = pit.data_uri_to_base64(part_value)
        user_args.append(image(b64))
      else:
        local_path = pit.resolve_local_path(part_value)
        _, b64 = pit.file_to_base64(local_path)
        user_args.append(image(b64))

  if structure is not None:
    schema_json = json.dumps(structure, indent=2)
    user_args.append(f"""

You MUST respond with valid JSON that matches this exact schema:
{schema_json}

Return ONLY the JSON object, no markdown formatting, no code blocks, no explanation.""")

  if not user_args:
    user_args = [""]

  return user_args


def GrokAIHook(prompt: str, structure: dict | None) -> tuple:
  """
    This function is called by the test runner to get the AI's response to a prompt.
    
    Prompt is the question to ask the AI.
    Structure contains the JSON schema for the expected output. If it is None, the output is just a string.
    
    There is no memory between calls to this function, the 'conversation' doesn't persist.
    
    Returns tuple of (result, chainOfThought).
    """
  from xai_sdk import Client
  from xai_sdk.chat import user

  try:
    # Initialize the client - uses XAI_API_KEY environment variable
    client = Client(timeout=3600)

    # Build chat creation parameters
    chat_params = {"model": MODEL}

    # Seems to have been removed from the API after grok-3
    # Map 0-10 scale to low/medium/high
    #model_has_builtin_reasoning = "reasoning" in MODEL.lower(
    #) and "non-reasoning" not in MODEL.lower()
    #if REASONING and REASONING != 0 and not model_has_builtin_reasoning:
    #    if isinstance(REASONING, int):
    #        if REASONING <= 3:
    #            chat_params["reasoning_effort"] = "low"
    #        elif REASONING <= 7:
    #            chat_params["reasoning_effort"] = "medium"
    #        else:
    #            chat_params["reasoning_effort"] = "high"
    #    else:
    #        chat_params["reasoning_effort"] = "medium"

    # Convert JSON schema to Pydantic model if provided
    pydantic_model = None
    if structure is not None:
      try:
        pydantic_model = json_schema_to_pydantic(structure, "ResponseModel")
      except Exception as e:
        print(f"Failed to convert schema to Pydantic: {e}")
        pydantic_model = None

    # Add tools if specified
    if TOOLS is True:
      chat_params["tools"] = [{
        "type": "web_search"
      }, {
        "type": "x_search"
      }, {
        "type": "code_execution"
      }]
    elif TOOLS and TOOLS is not False:
      if isinstance(TOOLS, list):
        chat_params["tools"] = TOOLS

    # Create chat and add user message
    chat = client.chat.create(**chat_params)

    user_args = build_xai_user_args(prompt, structure if pydantic_model is not None else None)
    chat.append(user(*user_args))

    # Stream response and accumulate (works for both structured and unstructured)
    chainOfThought = ""
    output_text = ""
    current_thinking_line = ""

    for response, chunk in chat.stream():
      # Check if this chunk contains reasoning/thinking content
      if hasattr(chunk, 'reasoning_content') and chunk.reasoning_content:
        current_thinking_line += chunk.reasoning_content
        while "\n" in current_thinking_line:
          line, current_thinking_line = current_thinking_line.split("\n", 1)
          print(f"Thinking: {line}", flush=True)
          chainOfThought += line + "\n"

      # Regular content
      if hasattr(chunk, 'content') and chunk.content:
        output_text += chunk.content

    # Flush any remaining thinking content
    if current_thinking_line:
      print(f"Thinking: {current_thinking_line}", flush=True)
      chainOfThought += current_thinking_line

    chainOfThought = chainOfThought.rstrip("\n")

    # Also check final response for reasoning content if not captured during streaming
    if not chainOfThought and hasattr(response, 'reasoning_content') and response.reasoning_content:
      chainOfThought = response.reasoning_content
      for line in chainOfThought.split("\n"):
        print(f"Thinking: {line}", flush=True)

    # Get final content from response if streaming didn't capture it
    if not output_text and hasattr(response, 'content'):
      output_text = response.content or ""

    if chainOfThought:
      print()  # Blank line after thinking

    # Parse structured output if we have a Pydantic model
    if pydantic_model is not None:
      try:
        # Strip markdown code blocks if present
        parse_text = output_text
        if "```json" in parse_text:
          parse_text = parse_text.split("```json", 1)[1].split("```", 1)[0]
        elif "```" in parse_text:
          parse_text = parse_text.split("```", 1)[1].split("```", 1)[0]

        parse_text = parse_text.strip()

        # Parse and validate with Pydantic
        parsed_obj = pydantic_model.model_validate_json(parse_text)
        result_dict = parsed_obj.model_dump()
        return result_dict, chainOfThought
      except Exception as e:
        print(f"Structured parse failed: {e}")
        return {}, ""
    else:
      # Non-structured output - just return the text
      return output_text or "", chainOfThought

  except Exception as e:
    print(f"Error calling xAI Grok API: {e}")

    # Check for content policy violation
    from ContentViolationHandler import is_content_violation_xai
    if is_content_violation_xai(e):
      print("CONTENT VIOLATION DETECTED (xAI Grok)")
      if structure is not None:
        return {"__content_violation__": True, "reason": str(e)}, f"Content violation: {e}"
      else:
        return "__content_violation__", f"Content violation: {e}"

    return None
