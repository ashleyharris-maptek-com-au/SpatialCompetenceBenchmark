def get_response(subPass: int):
  if subPass == 0:
    return {
      'shots': [{
        'bearing': 0,
        'elevation': 48,
        'speed': 16
      }, {
        'bearing': 0,
        'elevation': 35,
        'speed': 12.5
      }, {
        'bearing': 0,
        'elevation': 22,
        'speed': 16
      }]
    }, ""

  if subPass == 7:
    return {
      'shots': [{
        'bearing': 0,
        'elevation': 35,
        'speed': 13
      }, {
        'bearing': -2.5,
        'elevation': 30,
        'speed': 12.5
      }, {
        'bearing': 2.5,
        'elevation': 32,
        'speed': 13
      }]
    }, ""

  return None


def get_guess(subPass: int, rng):
  """Get a deterministic random guess for this question."""
  shots = []
  for _ in range(3):
    shots.append({
      "bearing": rng.uniform(-10.0, 10.0),
      "elevation": rng.uniform(5.0, 50.0),
      "speed": rng.uniform(10.0, 30.0),
    })
  return {"shots": shots}, "Random guess"

  if subPass == 1:
    return {
      'shots': [{
        'bearing': 1,
        'elevation': 5,
        'speed': 20
      }, {
        'bearing': 0,
        'elevation': 5,
        'speed': 20
      }, {
        'bearing': -1,
        'elevation': 5,
        'speed': 20
      }]
    }, ""

  if subPass == 2:
    return {
      'shots': [{
        'bearing': 0,
        'elevation': 35,
        'speed': 14
      }, {
        'bearing': 2,
        'elevation': 22,
        'speed': 13
      }, {
        'bearing': -2,
        'elevation': 22,
        'speed': 13
      }]
    }, ""

  if subPass == 3:
    return {
      'shots': [{
        'bearing': 0,
        'elevation': 42,
        'speed': 13
      }, {
        'bearing': 1,
        'elevation': 40,
        'speed': 13.5
      }, {
        'bearing': -1,
        'elevation': 44,
        'speed': 12.5
      }]
    }, ""

  if subPass == 4:
    return {
      'shots': [{
        'bearing': 8.5,
        'elevation': 38,
        'speed': 13.5
      }, {
        'bearing': -8.5,
        'elevation': 38,
        'speed': 13.5
      }, {
        'bearing': 0,
        'elevation': 30,
        'speed': 13
      }]
    }, ""

  if subPass == 5:
    return {
      'shots': [{
        'bearing': -8,
        'elevation': 25,
        'speed': 12
      }, {
        'bearing': 2,
        'elevation': 30,
        'speed': 13
      }, {
        'bearing': -8,
        'elevation': 20,
        'speed': 11
      }]
    }, ""
  if subPass == 6:
    return {
      'shots': [
        {
          'bearing': 0,
          'elevation': 5,
          'speed': 30
        },
        {
          'bearing': 0,
          'elevation': 10,
          'speed': 20
        },
        {
          'bearing': 0,
          'elevation': 50,
          'speed': 13
        },
      ]
    }, ""
  if subPass == 7:
    return {
      'shots': [{
        'bearing': 0,
        'elevation': 35,
        'speed': 13
      }, {
        'bearing': -2.5,
        'elevation': 30,
        'speed': 12.5
      }, {
        'bearing': 2.5,
        'elevation': 32,
        'speed': 13
      }]
    }, ""
