"""
Anthropic Claude AI Engine for MeshBenchmark

This module provides an interface to the Anthropic Claude API using the latest anthropic SDK.

Setup:
1. Install the SDK: pip install anthropic
2. Set your API key as an environment variable:
   - Windows: set ANTHROPIC_API_KEY=your_api_key_here
   - Linux/Mac: export ANTHROPIC_API_KEY=your_api_key_here
   
Get your API key from: https://console.anthropic.com/

The SDK documentation can be found at: https://github.com/anthropics/anthropic-sdk-python
"""

import os, json, hashlib
import PromptImageTagging as pit


class ClaudeEngine:
  """
  Anthropic Claude AI Engine class.
  
  Configuration parameters:
  - model: Model name (e.g., "claude-sonnet-4-20250514")
  - reasoning: Extended thinking mode (for supported models):
      - False: No extended thinking (default, faster)
      - integer 1-10: Enable extended thinking (deeper reasoning)
  - tools: Tool capabilities:
      - False: No tools available
      - True: Enable ALL built-in tools (web_search, code_execution)
      - List of tool definitions: Enable specific custom tools
  - prompt_caching: Enable caching for repeated content (default True)
  """

  def __init__(self, model: str, reasoning=False, tools=False, prompt_caching=True):
    self.model = model
    self.reasoning = reasoning
    self.tools = tools
    self.prompt_caching = prompt_caching
    self.configAndSettingsHash = hashlib.sha256(model.encode() + str(reasoning).encode() +
                                                str(tools).encode()).hexdigest()

  def AIHook(self, prompt: str, structure: dict | None) -> tuple:
    """Call the Claude API with instance configuration."""
    return _claude_ai_hook(prompt, structure, self.model, self.reasoning, self.tools,
                           self.prompt_caching)


def _build_anthropic_message_content(prompt: str) -> list[dict]:
  prompt_parts = pit.parse_prompt_parts(prompt)
  content_blocks: list[dict] = []
  for part_type, part_value in prompt_parts:
    if part_type == "text":
      if part_value:
        content_blocks.append({"type": "text", "text": part_value})
    elif part_type == "image":
      if pit.is_url(part_value):
        content_blocks.append({"type": "image", "source": {"type": "url", "url": part_value}})
      elif pit.is_data_uri(part_value):
        mime_type, b64 = pit.data_uri_to_base64(part_value)
        content_blocks.append({
          "type": "image",
          "source": {
            "type": "base64",
            "media_type": mime_type,
            "data": b64
          }
        })
      else:
        local_path = pit.resolve_local_path(part_value)
        mime_type, b64 = pit.file_to_base64(local_path)
        content_blocks.append({
          "type": "image",
          "source": {
            "type": "base64",
            "media_type": mime_type,
            "data": b64
          }
        })

  if not content_blocks:
    content_blocks = [{"type": "text", "text": ""}]

  return content_blocks


def _claude_ai_hook(prompt: str, structure: dict | None, model: str, reasoning, tools,
                    prompt_caching: bool) -> tuple:
  """
    This function is called by the test runner to get the AI's response to a prompt.
    
    Prompt is the question to ask the AI.
    Structure contains the JSON schema for the expected output. If it is None, the output is just a string.
    
    There is no memory between calls to this function, the 'conversation' doesn't persist.
    """
  from anthropic import Anthropic

  # Initialize the client - it will automatically use ANTHROPIC_API_KEY environment variable
  client = Anthropic()

  # Get the model's max tokens
  if "claude-sonnet-4-5" in model:
    max_tokens = 64000
  elif "claude-opus-4-5" in model:
    max_tokens = 64000
  else:
    max_tokens = 6400000

  try:
    betas = []
    if tools:
      betas.append("code-execution-2025-08-25")
    if structure:
      betas.append("structured-outputs-2025-11-13")

    content_blocks = _build_anthropic_message_content(prompt)

    # Build message parameters
    message_params = {
      "model": model,
      "max_tokens": max_tokens,
      "messages": [{
        "role": "user",
        "content": content_blocks
      }],
      "stream": True
    }

    if len(betas) > 0:
      message_params["betas"] = betas

    # Add tools if specified
    if tools is True:
      # Enable all built-in tools
      message_params["tools"] = [{
        "type": "web_search_20250305",
        "name": "web_search"
      }, {
        "type": "code_execution_20250825",
        "name": "code_execution"
      }]
    elif tools and tools is not False:
      # Custom tools provided
      message_params["tools"] = tools

    # Handle structured output using tools (Claude's approach)
    if structure is not None:

      # For some stupid reason, OpenAI requires "PropertyOrdering",
      # but Anthropic rejects it completely. Grrr
      def remove_property_ordering(schema):
        if isinstance(schema, dict):
          if "propertyOrdering" in schema:
            del schema["propertyOrdering"]

          if "maximum" in schema:
            del schema["maximum"]
          if "minimum" in schema:
            del schema["minimum"]
          if "minItems" in schema:
            del schema["minItems"]
          if "maxItems" in schema:
            del schema["maxItems"]
          for key, value in schema.items():
            remove_property_ordering(value)
        elif isinstance(schema, list):
          for item in schema:
            remove_property_ordering(item)

      remove_property_ordering(structure)

      message_params["output_format"] = {"type": "json_schema", "schema": structure}

    # Add thinking configuration if enabled (for supported models)
    if reasoning:
      # Extended thinking is enabled via model selection or beta headers
      # This is model-dependent and may require specific model versions
      message_params["thinking"] = {"type": "enabled", "budget_tokens": 32768 * reasoning // 10}

    # Handle prompt caching if enabled
    if prompt_caching:
      # Mark content for caching - last content block is typically cached
      # This requires modifying the content structure
      message_params["messages"][0]["content"][-1]["cache_control"] = {"type": "ephemeral"}

    # Make the API call
    responseStream = client.beta.messages.create(**message_params)

    chainOfThought = ""
    textOutput = ""
    thinkingBuffer = ""

    for content_block in responseStream:
      if content_block.type == "content_block_delta":
        if hasattr(content_block.delta, "thinking"):
          chainOfThought += content_block.delta.thinking
          thinkingBuffer += content_block.delta.thinking
          # Print complete lines from the buffer
          while '\n' in thinkingBuffer:
            line, thinkingBuffer = thinkingBuffer.split('\n', 1)
            print("Thinking: " + line)
        elif hasattr(content_block.delta, "text"):
          textOutput += content_block.delta.text

    #print(textOutput)

    if structure is not None:
      return json.loads(textOutput), chainOfThought
    else:
      return textOutput, chainOfThought

  except Exception as e:
    print(f"Error calling Claude API: {e}")

    # Check for content policy violation
    from ContentViolationHandler import is_content_violation_anthropic
    if is_content_violation_anthropic(e):
      print("CONTENT VIOLATION DETECTED (Anthropic)")
      if structure is not None:
        return {"__content_violation__": True, "reason": str(e)}, f"Content violation: {e}"
      else:
        return "__content_violation__", f"Content violation: {e}"

    # Return appropriate empty response based on structure
    if structure is not None:
      return {}, str(e)
    else:
      return "", str(e)


if __name__ == "__main__":
  engine = ClaudeEngine("claude-sonnet-4-5-20250929", False, False)
  print(engine.AIHook("What's the 7th prime number after 101?", None))

  engine = ClaudeEngine("claude-sonnet-4-5-20250929", True, True)
  print(engine.AIHook("What is the closest Australian city to New York?", None))

  print(
    engine.AIHook(
      "What is the furtherest Australian city from New York?", {
        "type": "object",
        "properties": {
          "cityName": {
            "type": "string"
          },
          "longitude": {
            "type": "number"
          },
          "latitude": {
            "type": "number"
          }
        },
        "required": ["cityName", "longitude", "latitude"],
        "additionalProperties": False
      }))
