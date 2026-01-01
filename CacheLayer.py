import os
import tempfile
import json
import hashlib
import datetime
import time
import random

from ContentViolationHandler import (is_prompt_blocked, block_prompt, is_violation_response)

# Global flag to bypass cache reading (still writes to cache)
FORCE_REFRESH = False

# Global flag to keep us offline.
OFFLINE_MODE = False

# Try very hard to get a cache hit, even if it means using old
# results months or years old.
POOR_MODE = True

# If the cache contains an empty result, ignore the cache and try again.
IGNORE_CACHED_FAILURES = False


class CacheLayer:

  def __init__(self, configAndSettingsHash, aiEngineHook, engineName: str = "Unknown"):
    self.hash = configAndSettingsHash
    self.aiEngineHook = aiEngineHook
    self.engineName = engineName
    self.temp_dir = tempfile.gettempdir()
    self.failCount = 0

  def AIHook(self, prompt: str, structure, index, subPass):
    # Check if this prompt is permanently blocked due to content violation
    if is_prompt_blocked(self.engineName, index, subPass, prompt):
      print(f"BLOCKED: Prompt for {self.engineName} Q{index}/S{subPass} is permanently blocked")
      if structure:
        return {
          "__content_violation__": True,
          "reason": "Previously blocked"
        }, "Content violation (blocked)"
      else:
        return "", "Content violation (blocked)"

    cacheDate = datetime.datetime.now()
    while True:
      h = (hashlib.sha256(prompt.strip().encode()).hexdigest(),
           hashlib.sha256(str(structure).encode()).hexdigest(), self.hash,
           cacheDate.strftime("%b %Y"))

      h = hashlib.sha256(str(h).encode()).hexdigest()

      cache_file = os.path.join(self.temp_dir, "cache_" + str(h) + ".txt")

      if POOR_MODE == False:
        break

      if os.path.exists(cache_file):
        break

      cacheDate -= datetime.timedelta(days=25)

      if cacheDate < datetime.datetime(2025, 11, 30):
        cacheDate = datetime.datetime.now()
        break

    if self.failCount > 3:
      if structure:
        return {}, "AI service has failed 9 times, assumed dead."
      else:
        return "", "AI service has failed 9 times, assumed dead."

    if not FORCE_REFRESH and os.path.exists(cache_file):
      try:
        with open(cache_file, "r", encoding="utf-8") as f:
          cachedJson = json.load(f)
        if len(str(cachedJson)) <= 6 and IGNORE_CACHED_FAILURES:
          print(f"IGNORE_CACHED_FAILURES set, cached result was too short: '{cachedJson}'")
          cachedJson = ""
          try:
            os.unlink(cache_file)
          except:
            pass

        if len(cachedJson) > 0:
          return cachedJson
      except Exception as e:
        print("Failed to read cache file: " + cache_file + " - " + str(e))
        try:
          os.unlink(cache_file)
        except:
          pass

    print("API Call: " + prompt[:100].replace("\n", " ") + "...")

    if OFFLINE_MODE:
      print("Offline mode: No API calls will be made, cache only.")
      return {}, ""

    print("Started at " + str(datetime.datetime.now()))
    result = self.aiEngineHook(prompt, structure)

    if not result and self.aiEngineHook.__name__ != "PlaceboAIHook":
      print("Empty result or Error 500, pausing and then retrying in a few minutes...")
      time.sleep(60 + random.randint(0, 120))
      result = self.aiEngineHook(prompt, structure)

      if not result:
        print(
          "Empty result or Error 500, pausing for a VERY LONG TIME and then retrying in a few minutes..."
        )
        time.sleep(600 + random.randint(0, 1200))
        result = self.aiEngineHook(prompt, structure)

    if not result:
      self.failCount += 1
      if structure:
        # We write an empty json object to the cache file so we don't keep retrying.
        with open(cache_file, "w", encoding="utf-8") as f:
          json.dump({}, f)
        return {}, "AI didn't respond after 3 retries - failing test"
      else:
        with open(cache_file, "w", encoding="utf-8") as f:
          json.dump("", f)
        return "", "AI didn't respond after 3 retries - failing test"

    print("Finished at " + str(datetime.datetime.now()))

    # Check if result indicates a content violation
    if result:
      result_data = result[0] if isinstance(result, tuple) else result
      if is_violation_response(result_data):
        reason = ""
        if isinstance(result_data, dict):
          reason = result_data.get("reason", "Content violation detected")
        block_prompt(self.engineName, index, subPass, prompt, reason)
        # Don't cache content violations - they're permanently blocked
        return result

    with open(cache_file, "w", encoding="utf-8") as f:
      json.dump(result, f)
    return result
