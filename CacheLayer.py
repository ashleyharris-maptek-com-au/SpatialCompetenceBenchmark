import os
import tempfile
import json
import hashlib
import datetime
import time
import random

# Global flag to bypass cache reading (still writes to cache)
FORCE_REFRESH = False

# Global flag to keep us offline.
OFFLINE_MODE = False


class CacheLayer:

    def __init__(self, configAndSettingsHash, aiEngineHook):
        self.hash = configAndSettingsHash
        self.aiEngineHook = aiEngineHook
        self.temp_dir = tempfile.gettempdir()
        self.failCount = 0

    def AIHook(self, prompt: str, structure, index, subPass):
        h = (hashlib.sha256(prompt.strip().encode()).hexdigest(),
             hashlib.sha256(str(structure).encode()).hexdigest(), self.hash,
             datetime.datetime.now().strftime("%b %Y"))

        h = hashlib.sha256(str(h).encode()).hexdigest()

        cache_file = os.path.join(self.temp_dir, "cache_" + str(h) + ".txt")

        if self.failCount > 3:
            if structure:
                return {}, "AI service has failed 9 times, assumed dead."
            else:
                return "", "AI service has failed 9 times, assumed dead."

        if not FORCE_REFRESH and os.path.exists(cache_file):
            try:
                with open(cache_file, "r", encoding="utf-8") as f:
                    cachedJson = json.load(f)
                    if len(cachedJson) > 0:
                        return cachedJson
            except Exception as e:
                print("Failed to read cache file: " + cache_file + " - " +
                      str(e))
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
            print(
                "Empty result or Error 500, pausing and then retrying in a few minutes..."
            )
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
                return {}, "AI didn't respond after 3 retries - failing test"
            else:
                return "", "AI didn't respond after 3 retries - failing test"

        print("Finished at " + str(datetime.datetime.now()))

        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump(result, f)
        return result
