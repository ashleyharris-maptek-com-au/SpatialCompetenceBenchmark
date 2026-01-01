def get_response(subPass: int):
  if subPass == 0:
    return {'groups': [[1, 2], [3, 4]]}, ""

  if subPass == 1:
    return {'groups': [[1], [2, 3, 4, 5, 6]]}, ""

  if subPass == 2:
    return {'groups': [[1], [2, 4, 5, 7], [3, 6, 8]]}, ""

  if subPass == 3:
    return {'groups': [[1, 5, 7], [2], [3, 4, 9, 10], [6, 8]]}, ""

  if subPass == 4:
    return {'groups': [[1, 10], [2, 5, 12], [3, 4, 11], [6], [7, 8, 9]]}, ""
  if subPass == 5:
    return {'groups': [[1, 9], [2, 12, 13], [3, 4, 6], [5, 7, 11, 16], [8, 14, 15], [10]]}, ""
  if subPass == 6:
    return {
      'groups': [[1, 15, 19], [2, 5, 9], [3, 4, 6, 14, 20], [7, 11], [8, 12, 13], [10, 16],
                 [17, 18]]
    }, ""
  if subPass == 7:
    return {
      'groups': [[1, 8, 11, 14, 15], [2, 10, 13], [3, 9, 12, 18, 24], [4, 7, 17, 22, 25],
                 [5, 6, 16, 23], [19], [20], [21]]
    }, ""
