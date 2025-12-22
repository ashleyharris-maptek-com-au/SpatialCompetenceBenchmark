import hashlib
from typing import Optional, Union
from placebo_data import get_response

configAndSettingsHash = hashlib.sha256(b"Placebo").hexdigest()


def PlaceboAIHook(prompt: str, structure: Optional[dict], questionNum: int,
                  subPass: int) -> Union[dict, str, None]:
  """Dispatch to the appropriate question module for placebo responses."""
  result = get_response(questionNum, subPass)
  if result is not None:
    return result

  # No response found for this question/subpass
  return None
