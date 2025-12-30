"""
Content Violation Handler

This module manages permanently blocked prompts that have triggered content policy
violations from AI providers. Once a prompt is blocked, it will never be retried.

The blocked prompts are stored in a JSON file in the repository.
"""

import os
import json
import hashlib
from typing import Optional, Tuple
from filelock import FileLock

BLOCKED_PROMPTS_FILE = os.path.join(os.path.dirname(__file__), "blocked_prompts.json")
BLOCKED_PROMPTS_LOCK = BLOCKED_PROMPTS_FILE + ".lock"


class ContentViolationError(Exception):
  """Exception raised when a content violation is detected."""

  def __init__(self, message: str, engine: str):
    self.message = message
    self.engine = engine
    super().__init__(message)


def compute_prompt_hash(prompt: str) -> str:
  """Compute a SHA256 hash of the prompt for storage."""
  return hashlib.sha256(prompt.strip().encode()).hexdigest()


def load_blocked_prompts() -> dict:
  """Load the blocked prompts database from disk."""
  if not os.path.exists(BLOCKED_PROMPTS_FILE):
    return {}

  try:
    with open(BLOCKED_PROMPTS_FILE, "r", encoding="utf-8") as f:
      return json.load(f)
  except (json.JSONDecodeError, IOError):
    return {}


def save_blocked_prompts(data: dict) -> None:
  """Save the blocked prompts database to disk with file locking."""
  lock = FileLock(BLOCKED_PROMPTS_LOCK, timeout=10)
  with lock:
    with open(BLOCKED_PROMPTS_FILE, "w", encoding="utf-8") as f:
      json.dump(data, f, indent=2, sort_keys=True)


def is_prompt_blocked(engine_name: str, question_index: int, subpass: int, prompt: str) -> bool:
  """
    Check if a prompt is blocked for a specific engine/question/subpass combination.
    
    Args:
        engine_name: Name of the AI engine
        question_index: The question/test index
        subpass: The subpass number
        prompt: The prompt text (used to compute hash)
    
    Returns:
        True if this prompt is blocked and should not be retried.
    """
  blocked = load_blocked_prompts()
  prompt_hash = compute_prompt_hash(prompt)

  key = f"{engine_name}:{question_index}:{subpass}:{prompt_hash}"
  return key in blocked


def block_prompt(engine_name: str, question_index: int, subpass: int, prompt: str,
                 reason: str) -> None:
  """
    Permanently block a prompt due to content violation.
    
    Args:
        engine_name: Name of the AI engine
        question_index: The question/test index
        subpass: The subpass number
        prompt: The prompt text
        reason: The reason/error message for the block
    """
  blocked = load_blocked_prompts()
  prompt_hash = compute_prompt_hash(prompt)

  key = f"{engine_name}:{question_index}:{subpass}:{prompt_hash}"

  if key not in blocked:
    blocked[key] = {
      "engine": engine_name,
      "question": question_index,
      "subpass": subpass,
      "prompt_hash": prompt_hash,
      "reason": reason,
      "blocked_at": __import__("datetime").datetime.now().isoformat()
    }
    save_blocked_prompts(blocked)
    print(f"CONTENT VIOLATION: Permanently blocked prompt for {engine_name} "
          f"Q{question_index}/S{subpass} - {reason[:100]}")


def is_content_violation_openai(error: Exception) -> bool:
  """Check if an OpenAI error is a content policy violation."""
  error_str = str(error).lower()
  error_repr = repr(error).lower()

  indicators = [
    "content_policy_violation", "content policy violation", "safety system",
    "content that is not allowed", "violated our policy", "violates our policy",
    "violating our usage policy", "violating our policy", "usage policy",
    "flagged as potentially violating"
  ]

  for indicator in indicators:
    if indicator in error_str or indicator in error_repr:
      return True

  # Check for error code in OpenAI error objects
  if hasattr(error, 'code') and error.code == "content_policy_violation":
    return True

  return False


def is_content_violation_anthropic(error: Exception) -> bool:
  """Check if an Anthropic error is a content policy violation."""
  error_str = str(error).lower()

  indicators = ["usage policy", "violate", "content policy", "not allowed", "harmful content"]

  # Need at least two indicators to avoid false positives
  matches = sum(1 for ind in indicators if ind in error_str)
  return matches >= 2 or ("violate" in error_str and "policy" in error_str)


def is_content_violation_gemini(error: Exception = None,
                                finish_reason: str = None,
                                block_reason: str = None) -> bool:
  """
    Check if a Gemini response indicates a content policy violation.
    
    Args:
        error: Exception if one was raised
        finish_reason: The finishReason from the response (e.g., "SAFETY")
        block_reason: The blockReason from promptFeedback
    """
  if finish_reason and finish_reason.upper() == "SAFETY":
    return True

  if block_reason:
    return True

  if error:
    error_str = str(error).lower()
    indicators = ["safety", "blocked", "content policy", "harm_category"]
    for indicator in indicators:
      if indicator in error_str:
        return True

  return False


def is_content_violation_bedrock(error: Exception) -> bool:
  """Check if an AWS Bedrock error is a content policy violation."""
  error_str = str(error).lower()
  error_repr = repr(error).lower()

  indicators = [
    "content moderation", "guardrail", "content filter", "blocked by", "harmful content",
    "violates", "not allowed"
  ]

  for indicator in indicators:
    if indicator in error_str or indicator in error_repr:
      return True

  # Check for specific Bedrock error types
  if hasattr(error, 'response'):
    error_code = error.response.get('Error', {}).get('Code', '')
    if error_code in ['ValidationException', 'AccessDeniedException']:
      # Check if it's content-related
      message = error.response.get('Error', {}).get('Message', '').lower()
      if any(ind in message for ind in indicators):
        return True

  return False


def is_content_violation_xai(error: Exception) -> bool:
  """Check if an xAI Grok error is a content policy violation."""
  error_str = str(error).lower()

  indicators = [
    "content policy",
    "violat",  # matches violate, violation, violated
    "not allowed",
    "safety",
    "harmful"
  ]

  for indicator in indicators:
    if indicator in error_str:
      return True

  return False


# Special return value to indicate content violation
CONTENT_VIOLATION_MARKER = {"__content_violation__": True}


def create_violation_response(structure: Optional[dict], reason: str) -> Tuple:
  """
    Create a response tuple indicating a content violation.
    
    Returns a tuple of (result, chainOfThought) where result contains
    the violation marker.
    """
  if structure is not None:
    return ({"__content_violation__": True, "reason": reason}, f"Content violation: {reason}")
  else:
    return ("", f"Content violation: {reason}")


def is_violation_response(result) -> bool:
  """Check if a result is a content violation marker."""
  if isinstance(result, dict) and result.get("__content_violation__"):
    return True
  return False
