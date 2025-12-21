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

# Constants that fine tune which model, reasoning mode, and tools
# Example model IDs:
#   - qwen.qwen3-30b-a3b-v1:0
#   - qwen.qwen3-235b-a22b-v1:0
#   - anthropic.claude-3-sonnet-20240229-v1:0
#   - anthropic.claude-3-5-sonnet-20241022-v2:0
#   - meta.llama3-70b-instruct-v1:0
#   - mistral.mistral-large-2402-v1:0
MODEL = "qwen.qwen3-30b-a3b-v1:0"

# REASONING controls reasoning/thinking mode:
# - False or 0: No special reasoning (standard mode)
# - Integer (1-10): Reasoning effort level (model-dependent)
# Note: Not all Bedrock models support extended thinking
REASONING = False

# TOOLS enables tool capabilities:
# - False: No tools available
# - True: Enable tool use (model must support it)
# - List of tool definitions: Enable specific custom tools
TOOLS = False

# AWS Region for Bedrock
REGION = "us-east-1"

configAndSettingsHash = hashlib.sha256(MODEL.encode() + str(REASONING).encode() +
                                       str(TOOLS).encode() + REGION.encode()).hexdigest()

forcedFailure = False


def Configure(Model, Reasoning, Tools, Region=None):
  global MODEL
  global REASONING
  global TOOLS
  global REGION
  global configAndSettingsHash
  global forcedFailure
  MODEL = Model
  REASONING = Reasoning
  TOOLS = Tools
  if Region:
    REGION = Region
  forcedFailure = False
  configAndSettingsHash = hashlib.sha256(MODEL.encode() + str(REASONING).encode() +
                                         str(TOOLS).encode() + REGION.encode()).hexdigest()


import os
import json
import PromptImageTagging as pit


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


def BedrockAIHook(prompt: str, structure: dict | None) -> tuple:
  """
    This function is called by the test runner to get the AI's response to a prompt.
    
    Prompt is the question to ask the AI.
    Structure contains the JSON schema for the expected output. If it is None, the output is just a string.
    
    There is no memory between calls to this function, the 'conversation' doesn't persist.
    
    Returns tuple of (result, chainOfThought).
    """
  global forcedFailure

  if forcedFailure:
    return {"error": "Forced failure"}, "Forced failure due to API instability"

  import boto3
  from botocore.exceptions import ClientError

  try:
    # Initialize the Bedrock runtime client
    client = boto3.client(service_name='bedrock-runtime', region_name=REGION)

    # Build content blocks
    content_blocks = build_bedrock_content(prompt)

    # Build messages
    messages = [{"role": "user", "content": content_blocks}]

    # Build inference config
    inference_config = {"temperature": 0.7, "maxTokens": 8192}

    if MODEL in ["meta.llama3-70b-instruct-v1:0"]:
      inference_config["maxTokens"] = 2048

    # Additional model-specific fields
    additional_fields = {}

    # Handle reasoning/thinking for models that support it
    if REASONING and isinstance(REASONING, int) and REASONING > 0:
      # Some models support thinking/reasoning parameters
      # This is model-dependent - Qwen models may use different parameters
      if "qwen" in MODEL.lower():
        # Qwen models may support thinking mode via system prompt or parameters
        additional_fields["enable_thinking"] = True
      elif "claude" in MODEL.lower():
        # Claude on Bedrock may support extended thinking
        pass  # Handled differently

    # If structured output is requested, add schema instruction to prompt
    if structure is not None:
      schema_json = json.dumps(structure, indent=2)
      schema_instruction = f"""

You MUST respond with valid JSON that matches this exact schema:
{schema_json}

Return ONLY the JSON object, no markdown formatting, no code blocks, no explanation."""

      # Append to last text block or add new one
      if content_blocks and "text" in content_blocks[-1]:
        content_blocks[-1]["text"] += schema_instruction
      else:
        content_blocks.append({"text": schema_instruction})

      # Update messages with modified content
      messages = [{"role": "user", "content": content_blocks}]

    # Build tool config if tools are enabled
    tool_config = None
    if TOOLS is True:
      # Enable default tools - model dependent
      pass  # Bedrock tool use requires specific tool definitions
    elif TOOLS and TOOLS is not False and isinstance(TOOLS, list):
      tool_config = {"tools": TOOLS}

    # Use streaming for real-time output
    converse_params = {"modelId": MODEL, "messages": messages, "inferenceConfig": inference_config}

    if additional_fields:
      converse_params["additionalModelRequestFields"] = additional_fields

    if tool_config:
      converse_params["toolConfig"] = tool_config

    # Stream the response
    response = client.converse_stream(**converse_params)

    chainOfThought = ""
    output_text = ""
    current_thinking_line = ""

    stream = response.get('stream')
    if stream:
      for event in stream:
        # Handle message start
        if 'messageStart' in event:
          pass  # Role info

        # Handle content block delta (main text output)
        if 'contentBlockDelta' in event:
          delta = event['contentBlockDelta'].get('delta', {})
          if 'text' in delta:
            output_text += delta['text']
          # Some models may include reasoning in a separate field
          if 'reasoningContent' in delta:
            thinking = delta['reasoningContent'].get('text', '')
            current_thinking_line += thinking
            while "\n" in current_thinking_line:
              line, current_thinking_line = current_thinking_line.split("\n", 1)
              print(f"Thinking: {line}", flush=True)
              chainOfThought += line + "\n"

        # Handle content block start (may indicate thinking vs output)
        if 'contentBlockStart' in event:
          block_start = event['contentBlockStart']
          # Check if this is a thinking/reasoning block
          if 'start' in block_start:
            start_info = block_start['start']
            if 'reasoningContent' in start_info:
              pass  # Reasoning block starting

        # Handle message stop
        if 'messageStop' in event:
          pass  # Stop reason

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
    if structure is not None:
      if output_text:
        # Try to extract JSON from output
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
          return json.loads(json_text), chainOfThought
        except json.JSONDecodeError as e:
          print(f"Warning: Failed to parse JSON response: {e}")
          print(f"Raw output was: {output_text[:500]}")
          return {}, chainOfThought
      return {}, chainOfThought
    else:
      return output_text or "", chainOfThought

  except ClientError as err:
    error_message = err.response['Error']['Message']
    print(f"AWS Bedrock client error: {error_message}")
    if structure is not None:
      return {}, str(err)
    else:
      return "", str(err)

  except Exception as e:
    print(f"Error calling Amazon Bedrock API: {e}")
    if structure is not None:
      return {}, str(e)
    else:
      return "", str(e)


if __name__ == "__main__":
  # Test with Qwen3
  Configure("qwen.qwen3-30b-a3b-v1:0", False, False, "us-east-1")
  print("Testing Qwen3 on Bedrock...")
  result, cot = BedrockAIHook("What is 2 + 2? Answer briefly.", None)
  print(f"Result: {result}")
  print(f"Chain of Thought: {cot}")

  # Test structured output
  print("\nTesting structured output...")
  result, cot = BedrockAIHook(
    "What is the capital of France?", {
      "type": "object", "properties": {"city": {"type": "string"}, "country": {"type": "string"}},
      "required": ["city", "country"]
    })
  print(f"Structured Result: {result}")
