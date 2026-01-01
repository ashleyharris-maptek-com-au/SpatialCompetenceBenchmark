import hashlib
from typing import Optional, Union
from placebo_data import get_response


class PlaceboEngine:
  """
  Placebo AI Engine class for testing with pre-defined responses.
  
  This engine returns pre-defined "human with tools" responses for benchmark tests.
  It doesn't make any API calls.
  """

  def __init__(self):
    self.configAndSettingsHash = hashlib.sha256(b"Placebo").hexdigest()

  def AIHook(self, prompt: str, structure: Optional[dict], questionNum: int,
             subPass: int) -> Union[dict, str, None]:
    """Dispatch to the appropriate question module for placebo responses."""
    result = get_response(questionNum, subPass)
    if result is not None:
      return result

    # No response found for this question/subpass
    return None
