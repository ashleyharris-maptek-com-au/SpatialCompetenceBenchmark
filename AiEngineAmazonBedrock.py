"""
Amazon Bedrock AI Engine for MeshBenchmark

This module provides an interface to Amazon Bedrock using the Converse API.
Supports models like Qwen3, Claude, Llama, Mistral, and others available on Bedrock.

Setup:
1. Install the SDK: pip install boto3
2. Configure AWS credentials:
   - AWS CLI: aws configure
   - Or set environment variables:
     - AWS_ACCESS_KEY_ID=your_access_key
     - AWS_SECRET_ACCESS_KEY=your_secret_key
     - AWS_DEFAULT_REGION=us-east-1 (or your preferred region)
   
Get access from: https://console.aws.amazon.com/bedrock/

The Bedrock documentation: https://docs.aws.amazon.com/bedrock/latest/userguide/
"""

import hashlib
import os
import json
import PromptImageTagging as pit
from typing import Any, List, Optional
from pydantic import BaseModel, create_model


class BedrockEngine:
  """
  Amazon Bedrock AI Engine class.
  
  Configuration parameters:
  - model: Model ID (e.g., "qwen.qwen3-30b-a3b-v1:0", "meta.llama3-70b-instruct-v1:0")
  - reasoning: Reasoning/thinking mode:
      - False or 0: No special reasoning (standard mode)
      - Integer (1-10): Reasoning effort level (model-dependent)
  - tools: Tool capabilities:
      - False: No tools available
      - True: Enable hosted tools (Nova: code_interpreter + web_grounding)
      - List of tool definitions: Enable specific custom tools
  - region: AWS Region for Bedrock (default "us-east-1")
  - flex_tier: Use Flex service tier for cost savings (default False)
  """

  def __init__(self, model: str, reasoning=False, tools=False, region="us-east-1", flex_tier=False):
    self.model = model
    self.reasoning = reasoning
    self.tools = tools
    self.region = region
    self.flex_tier = flex_tier
    self.forcedFailure = False
    self.configAndSettingsHash = hashlib.sha256(model.encode() + str(reasoning).encode() +
                                                str(tools).encode()).hexdigest()

  def AIHook(self, prompt: str, structure: dict | None) -> tuple:
    """Call the Bedrock API with instance configuration."""
    return _bedrock_ai_hook(prompt, structure, self.model, self.reasoning, self.tools, self.region,
                            self.flex_tier, self)


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


def build_bedrock_content(prompt: str) -> list[dict]:
  """Build Bedrock Converse API content blocks from prompt with image tags."""
  prompt_parts = pit.parse_prompt_parts(prompt)
  content_blocks: list[dict] = []

  for part_type, part_value in prompt_parts:
    if part_type == "text":
      if part_value:
        content_blocks.append({"text": part_value})
    elif part_type == "image":
      if pit.is_url(part_value):
        # Bedrock doesn't support URLs directly, need to download
        from urllib.request import Request, urlopen
        req = Request(part_value, headers={"User-Agent": "MeshBenchmark/1.0"})
        with urlopen(req, timeout=30) as resp:
          image_bytes = resp.read()
          content_type = resp.headers.get("Content-Type", "")

        # Determine format from content type or URL
        if "jpeg" in content_type or "jpg" in content_type:
          img_format = "jpeg"
        elif "png" in content_type:
          img_format = "png"
        elif "gif" in content_type:
          img_format = "gif"
        elif "webp" in content_type:
          img_format = "webp"
        else:
          # Guess from URL
          ext = part_value.split(".")[-1].lower()
          img_format = "jpeg" if ext in ["jpg", "jpeg"] else ext

        content_blocks.append({"image": {"format": img_format, "source": {"bytes": image_bytes}}})
      elif pit.is_data_uri(part_value):
        mime_type, image_bytes = pit.decode_data_uri(part_value)
        img_format = mime_type.split("/")[-1]
        if img_format == "jpg":
          img_format = "jpeg"
        content_blocks.append({"image": {"format": img_format, "source": {"bytes": image_bytes}}})
      else:
        # Local file path
        local_path = pit.resolve_local_path(part_value)
        image_bytes = pit.read_file_bytes(local_path)
        ext = os.path.splitext(local_path)[1].lower().lstrip(".")
        img_format = "jpeg" if ext in ["jpg", "jpeg"] else ext
        content_blocks.append({"image": {"format": img_format, "source": {"bytes": image_bytes}}})

  if not content_blocks:
    content_blocks = [{"text": ""}]

  return content_blocks


def _bedrock_ai_hook(prompt: str, structure: Optional[dict], model: str, reasoning, tools,
                     region: str, flex_tier: bool, engine_instance) -> tuple:
  """
    This function is called by the test runner to get the AI's response to a prompt.
    
    Prompt is the question to ask the AI.
    Structure contains the JSON schema for the expected output. If it is None, the output is just a string.
    
    There is no memory between calls to this function, the 'conversation' doesn't persist.
    
    Returns tuple of (result, chainOfThought).
    """
  if engine_instance.forcedFailure:
    return {"error": "Forced failure"}, "Forced failure due to API instability"

  import boto3
  from botocore.exceptions import ClientError

  try:
    # Initialize the Bedrock runtime client
    client = boto3.client(service_name='bedrock-runtime', region_name=region)

    # Build content blocks
    content_blocks = build_bedrock_content(prompt)

    # Build messages
    messages = [{"role": "user", "content": content_blocks}]

    # Build inference config
    inference_config = {"temperature": 0.7, "maxTokens": 8192}

    if model in ["meta.llama3-70b-instruct-v1:0", "meta.llama3-1-405b-instruct-v1:0"]:
      inference_config["maxTokens"] = 2048
    elif "nova" in model.lower():
      inference_config["maxTokens"] = 10000

    # Additional model-specific fields
    additional_fields = {}

    # Handle reasoning/thinking for models that support it
    if reasoning and isinstance(reasoning, int) and reasoning > 0:
      # Some models support thinking/reasoning parameters
      # This is model-dependent - Qwen models may use different parameters
      if "qwen" in model.lower():
        # Qwen models may support thinking mode via system prompt or parameters
        additional_fields["enable_thinking"] = True
      elif "claude" in model.lower():
        # Claude on Bedrock may support extended thinking
        pass  # Handled differently

    # Build tool config
    tool_config = None
    use_tool_for_structure = False

    # If structured output is requested, use Tool Use approach for better reliability
    if structure is not None:
      # Create a tool definition with the JSON schema as its input schema
      # This forces the model to output structured data matching the schema
      structured_tool = {
        "toolSpec": {
          "name": "structured_response",
          "description":
          "Submit your response in the required structured format. You MUST call this tool with your complete answer.",
          "inputSchema": {
            "json": structure
          }
        }
      }

      tool_config = {"tools": [structured_tool]}
      # Force the model to use this specific tool
      tool_config["toolChoice"] = {"tool": {"name": "structured_response"}}
      use_tool_for_structure = True

      # Also add instruction to prompt for clarity
      schema_instruction = "\n\nYou must call the 'structured_response' tool with your complete answer."
      if content_blocks and "text" in content_blocks[-1]:
        content_blocks[-1]["text"] += schema_instruction
      else:
        content_blocks.append({"text": schema_instruction})
      messages = [{"role": "user", "content": content_blocks}]

    # Add other tools if enabled (but don't override structured output tool)
    if not use_tool_for_structure:
      if tools is True:
        # Enable Nova hosted tools: code interpreter and web grounding
        if "nova" in model.lower():
          tool_config = {
            "tools": [{
              "systemTool": {
                "name": "nova_code_interpreter"
              }
            }, {
              "systemTool": {
                "name": "nova_grounding"
              }
            }]
          }
      elif tools and tools is not False and isinstance(tools, list):
        tool_config = {"tools": tools}

    # Use streaming for real-time output
    converse_params = {"modelId": model, "messages": messages, "inferenceConfig": inference_config}

    # Apply flex tier if enabled (discounted pricing, may have delays)
    if flex_tier:
      converse_params["performanceConfig"] = {"serviceTier": "flex"}

    if additional_fields:
      converse_params["additionalModelRequestFields"] = additional_fields

    if tool_config:
      converse_params["toolConfig"] = tool_config

    # Stream the response
    response = client.converse_stream(**converse_params)

    chainOfThought = ""
    output_text = ""
    current_thinking_line = ""
    tool_use_input = ""  # For capturing tool use structured data
    current_tool_name = None
    stop_reason = None

    stream = response.get('stream')
    chunk_count = 0
    if stream:
      for event in stream:
        chunk_count += 1
        # Handle message start
        if 'messageStart' in event:
          pass  # Role info

        # Handle content block start (may indicate tool use or thinking)
        if 'contentBlockStart' in event:
          block_start = event['contentBlockStart']
          if 'start' in block_start:
            start_info = block_start['start']
            if 'reasoningContent' in start_info:
              pass  # Reasoning block starting
            # Check for tool use start
            if 'toolUse' in start_info:
              current_tool_name = start_info['toolUse'].get('name')
              tool_use_input = ""  # Reset for new tool call
              print(f"Tool use started: {current_tool_name}")

        # Handle content block delta (main text output or tool input)
        if 'contentBlockDelta' in event:
          delta = event['contentBlockDelta'].get('delta', {})
          if 'text' in delta:
            output_text += delta['text']
          # Tool use input comes as JSON string chunks
          if 'toolUse' in delta:
            chunk_input = delta['toolUse'].get('input', '')
            tool_use_input += chunk_input
            if len(tool_use_input) < 200:  # Only log for small amounts
              print(f"Tool input chunk: {chunk_input[:100]}")
          # Some models may include reasoning in a separate field
          if 'reasoningContent' in delta:
            thinking = delta['reasoningContent'].get('text', '')
            current_thinking_line += thinking
            while "\n" in current_thinking_line:
              line, current_thinking_line = current_thinking_line.split("\n", 1)
              print(f"Thinking: {line}", flush=True)
              chainOfThought += line + "\n"

        # Handle message stop
        if 'messageStop' in event:
          stop_reason = event['messageStop'].get('stopReason', 'unknown')
          print(f"Stream stopped: {stop_reason}")

        # Handle metadata (token usage, etc.)
        if 'metadata' in event:
          metadata = event['metadata']
          if 'usage' in metadata:
            usage = metadata['usage']
            print(f"Tokens - Input: {usage.get('inputTokens', 'N/A')}, "
                  f"Output: {usage.get('outputTokens', 'N/A')}")

    # Flush remaining thinking content
    if current_thinking_line:
      print(f"Thinking: {current_thinking_line}", flush=True)
      chainOfThought += current_thinking_line

    chainOfThought = chainOfThought.rstrip("\n")

    # Parse response
    print(f"Total output length: {len(output_text)} chars, tool_use: {len(tool_use_input)} chars")
    if structure is not None:
      # Prefer tool use input (from forced tool call) over text output
      if use_tool_for_structure and tool_use_input:
        # Tool use provides structured data directly
        try:
          # The tool input should already be valid JSON matching our schema
          parsed_data = json.loads(tool_use_input)
          # Validate with Pydantic
          pydantic_model = json_schema_to_pydantic(structure, "ResponseModel")
          parsed_obj = pydantic_model.model_validate(parsed_data)
          return parsed_obj.model_dump(), chainOfThought
        except Exception as e:
          print(f"Warning: Tool use input failed validation: {e}")
          print(f"Tool use input was: {tool_use_input[:500]}")
          # Fall through to try text output

      # Fallback: try to extract JSON from text output
      if output_text:
        json_text = output_text.strip()

        # Strip markdown code blocks if present
        if json_text.startswith("```json"):
          json_text = json_text[7:]
        if json_text.startswith("```"):
          json_text = json_text[3:]
        if json_text.endswith("```"):
          json_text = json_text[:-3]
        json_text = json_text.strip()

        try:
          # Use Pydantic for full schema validation
          pydantic_model = json_schema_to_pydantic(structure, "ResponseModel")
          parsed_obj = pydantic_model.model_validate_json(json_text)
          return parsed_obj.model_dump(), chainOfThought
        except Exception as e:
          print(f"Warning: Failed to validate JSON response against schema: {e}")
          print(f"Raw output was: {output_text[:500]}")
          return {}, chainOfThought
      return {}, chainOfThought
    else:
      return output_text or "", chainOfThought

  except ClientError as err:
    error_message = err.response['Error']['Message']
    print(f"AWS Bedrock client error: {error_message}")

    # Check for content policy violation
    from ContentViolationHandler import is_content_violation_bedrock
    if is_content_violation_bedrock(err):
      print("CONTENT VIOLATION DETECTED (Bedrock)")
      if structure is not None:
        return {"__content_violation__": True, "reason": str(err)}, f"Content violation: {err}"
      else:
        return "__content_violation__", f"Content violation: {err}"

    if structure is not None:
      return {}, str(err)
    else:
      return "", str(err)

  except Exception as e:
    print(f"Error calling Amazon Bedrock API: {e}")

    # Check for content policy violation
    from ContentViolationHandler import is_content_violation_bedrock
    if is_content_violation_bedrock(e):
      print("CONTENT VIOLATION DETECTED (Bedrock)")
      if structure is not None:
        return {"__content_violation__": True, "reason": str(e)}, f"Content violation: {e}"
      else:
        return "__content_violation__", f"Content violation: {e}"

    if structure is not None:
      return {}, str(e)
    else:
      return "", str(e)


if __name__ == "__main__":
  # Test with Qwen3
  engine = BedrockEngine("qwen.qwen3-30b-a3b-v1:0", False, False, "us-east-1")
  print("Testing Qwen3 on Bedrock...")
  result, cot = engine.AIHook("What is 2 + 2? Answer briefly.", None)
  print(f"Result: {result}")
  print(f"Chain of Thought: {cot}")

  # Test structured output
  print("\nTesting structured output...")
  result, cot = engine.AIHook(
    "What is the capital of France?", {
      "type": "object",
      "properties": {
        "city": {
          "type": "string"
        },
        "country": {
          "type": "string"
        }
      },
      "required": ["city", "country"]
    })
  print(f"Structured Result: {result}")
