def get_response(subPass: int):
  return {
    "q1": False,
    "q2": False,
    "q3": False,
    "q4": False,
    "q5": 1 if subPass >= 2 else 0,
    "imageDescription": "Something SFW"
  }, ""
