import math
from textwrap import dedent


def get_response(subPass: int):
    """Get the placebo response for this question."""
    if True:  # Catch-all for any subpass
        g = {}
        exec(open("24.py").read(), g)
        count = g["pointsCount"][subPass]
        pts = g["points"][:count]

        from scipy.spatial import ConvexHull
        hull = ConvexHull(pts)
        return {"pointSequence": hull.vertices.tolist(), "reasoning": "SciPy is a tool."}, ""

    if subPass == 4:
        return {
                'reasoning':
                'Create three stepped, walled catchments in a line to the east of the rainfall point. Lake A (highest) surrounds the centre fall point and is dammed up to z=6, with only a small spillway opening at z=6 into Lake B. Lake B is dammed up to z=5 with a spillway at z=5 into Lake C. Lake C is dammed up to z=4 with a spillway at z=4 directly to the map edge so excess water is safely lost. During heavy rain, water fills A layer-by-layer and overflows only when it reaches z=6, then B overflows at z=5, and C sheds any z=4 water off-map. After rain stops and the system settles, the spill layers drain away, leaving stable pool surfaces at z=5 (A), z=4 (B), and z=3 (C): three lakes on three distinct z-levels.',
                'voxels': [{'xyz': [19, 19, 3], 'material':
                                        'Dirt'}, {'xyz': [20, 19, 3], 'material':
                                                            'Dirt'}, {'xyz': [21, 19, 3], 'material':
                                                                                'Dirt'}, {'xyz': [22, 19, 3], 'material':
                                                                                                    'Dirt'}, {'xyz': [23, 19, 3], 'material': 'Dirt'},
                                      {'xyz': [24, 19, 3], 'material':
                                        'Dirt'}, {'xyz': [25, 19, 3], 'material':
                                                            'Dirt'}, {'xyz': [26, 19, 3], 'material':
                                                                                'Dirt'}, {'xyz': [27, 19, 3], 'material':
                                                                                                    'Dirt'}, {'xyz': [28, 19, 3], 'material': 'Dirt'},
                                      {'xyz': [29, 19, 3], 'material':
                                        'Dirt'}, {'xyz': [30, 19, 3], 'material':
                                                            'Dirt'}, {'xyz': [31, 19, 3], 'material':
                                                                                'Dirt'}, {'xyz': [32, 19, 3], 'material':
                                                                                                    'Dirt'}, {'xyz': [33, 19, 3], 'material': 'Dirt'},
                                      {'xyz': [34, 19, 3], 'material':
                                        'Dirt'}, {'xyz': [35, 19, 3], 'material':
                                                            'Dirt'}, {'xyz': [36, 19, 3], 'material':
                                                                                'Dirt'}, {'xyz': [37, 19, 3], 'material':
                                                                                                    'Dirt'}, {'xyz': [38, 19, 3], 'material': 'Dirt'},
                                      {'xyz': [39, 19, 3], 'material':
                                        'Dirt'}, {'xyz': [40, 19, 3], 'material':
                                                            'Dirt'}, {'xyz': [41, 19, 3], 'material':
                                                                                'Dirt'}, {'xyz': [42, 19, 3], 'material':
                                                                                                    'Dirt'}, {'xyz': [43, 19, 3], 'material': 'Dirt'},
                                      {'xyz': [44, 19, 3], 'material':
                                        'Dirt'}, {'xyz': [45, 19, 3], 'material':
                                                            'Dirt'}, {'xyz': [46, 19, 3], 'material':
                                                                                'Dirt'}, {'xyz': [19, 20, 3], 'material':
                                                                                                    'Dirt'}, {'xyz': [28, 20, 3], 'material': 'Dirt'},
                                      {'xyz': [37, 20, 3], 'material':
                                        'Dirt'}, {'xyz': [46, 20, 3], 'material':
                                                            'Dirt'}, {'xyz': [19, 21, 3], 'material':
                                                                                'Dirt'}, {'xyz': [28, 21, 3], 'material':
                                                                                                    'Dirt'}, {'xyz': [37, 21, 3], 'material': 'Dirt'},
                                      {'xyz': [46, 21, 3], 'material':
                                        'Dirt'}, {'xyz': [19, 22, 3], 'material':
                                                            'Dirt'}, {'xyz': [28, 22, 3], 'material':
                                                                                'Dirt'}, {'xyz': [37, 22, 3], 'material':
                                                                                                    'Dirt'}, {'xyz': [46, 22, 3], 'material': 'Dirt'},
                                      {'xyz': [19, 23, 3], 'material':
                                        'Dirt'}, {'xyz': [28, 23, 3], 'material':
                                                            'Dirt'}, {'xyz': [37, 23, 3], 'material':
                                                                                'Dirt'}, {'xyz': [46, 23, 3], 'material':
                                                                                                    'Dirt'}, {'xyz': [19, 24, 3], 'material': 'Dirt'},
                                      {'xyz': [28, 24, 3], 'material':
                                        'Dirt'}, {'xyz': [37, 24, 3], 'material':
                                                            'Dirt'}, {'xyz': [46, 24, 3], 'material':
                                                                                'Dirt'}, {'xyz': [19, 25, 3], 'material':
                                                                                                    'Dirt'}, {'xyz': [28, 25, 3], 'material': 'Dirt'},
                                      {'xyz': [37, 25, 3], 'material':
                                        'Dirt'}, {'xyz': [46, 25, 3], 'material':
                                                            'Dirt'}, {'xyz': [19, 26, 3], 'material':
                                                                                'Dirt'}, {'xyz': [28, 26, 3], 'material':
                                                                                                    'Dirt'}, {'xyz': [37, 26, 3], 'material': 'Dirt'},
                                      {'xyz': [46, 26, 3], 'material':
                                        'Dirt'}, {'xyz': [19, 27, 3], 'material':
                                                            'Dirt'}, {'xyz': [28, 27, 3], 'material':
                                                                                'Dirt'}, {'xyz': [37, 27, 3], 'material':
                                                                                                    'Dirt'}, {'xyz': [46, 27, 3], 'material': 'Dirt'},
                                      {'xyz': [19, 28, 3], 'material':
                                        'Dirt'}, {'xyz': [20, 28, 3], 'material':
                                                            'Dirt'}, {'xyz': [21, 28, 3], 'material':
                                                                                'Dirt'}, {'xyz': [22, 28, 3], 'material':
                                                                                                    'Dirt'}, {'xyz': [23, 28, 3], 'material': 'Dirt'},
                                      {'xyz': [24, 28, 3], 'material':
                                        'Dirt'}, {'xyz': [25, 28, 3], 'material':
                                                            'Dirt'}, {'xyz': [26, 28, 3], 'material':
                                                                                'Dirt'}, {'xyz': [27, 28, 3], 'material':
                                                                                                    'Dirt'}, {'xyz': [28, 28, 3], 'material': 'Dirt'},
                                      {'xyz': [29, 28, 3], 'material':
                                        'Dirt'}, {'xyz': [30, 28, 3], 'material':
                                                            'Dirt'}, {'xyz': [31, 28, 3], 'material':
                                                                                'Dirt'}, {'xyz': [32, 28, 3], 'material':
                                                                                                    'Dirt'}, {'xyz': [33, 28, 3], 'material': 'Dirt'},
                                      {'xyz': [34, 28, 3], 'material':
                                        'Dirt'}, {'xyz': [35, 28, 3], 'material':
                                                            'Dirt'}, {'xyz': [36, 28, 3], 'material':
                                                                                'Dirt'}, {'xyz': [37, 28, 3], 'material':
                                                                                                    'Dirt'}, {'xyz': [38, 28, 3], 'material': 'Dirt'},
                                      {'xyz': [39, 28, 3], 'material':
                                        'Dirt'}, {'xyz': [40, 28, 3], 'material':
                                                            'Dirt'}, {'xyz': [41, 28, 3], 'material':
                                                                                'Dirt'}, {'xyz': [42, 28, 3], 'material':
                                                                                                    'Dirt'}, {'xyz': [43, 28, 3], 'material': 'Dirt'},
                                      {'xyz': [44, 28, 3], 'material':
                                        'Dirt'}, {'xyz': [45, 28, 3], 'material':
                                                            'Dirt'}, {'xyz': [46, 28, 3], 'material':
                                                                                'Dirt'}, {'xyz': [19, 19, 4], 'material':
                                                                                                    'Dirt'}, {'xyz': [20, 19, 4], 'material': 'Dirt'},
                                      {'xyz': [21, 19, 4], 'material':
                                        'Dirt'}, {'xyz': [22, 19, 4], 'material':
                                                            'Dirt'}, {'xyz': [23, 19, 4], 'material':
                                                                                'Dirt'}, {'xyz': [24, 19, 4], 'material':
                                                                                                    'Dirt'}, {'xyz': [25, 19, 4], 'material': 'Dirt'},
                                      {'xyz': [26, 19, 4], 'material':
                                        'Dirt'}, {'xyz': [27, 19, 4], 'material':
                                                            'Dirt'}, {'xyz': [28, 19, 4], 'material':
                                                                                'Dirt'}, {'xyz': [29, 19, 4], 'material':
                                                                                                    'Dirt'}, {'xyz': [30, 19, 4], 'material': 'Dirt'},
                                      {'xyz': [31, 19, 4], 'material':
                                        'Dirt'}, {'xyz': [32, 19, 4], 'material':
                                                            'Dirt'}, {'xyz': [33, 19, 4], 'material':
                                                                                'Dirt'}, {'xyz': [34, 19, 4], 'material': 'Dirt'}, {
                                                                                        'xyz': [35, 19,
                                                                                                        4], 'material': 'Dirt'
                                                                                }, {'xyz': [36, 19, 4], 'material':
                                                                                        'Dirt'}, {'xyz': [37, 19, 4], 'material': 'Dirt'
                                                                                                            }, {'xyz': [38, 19, 4], 'material': 'Dirt'},
                                      {'xyz': [39, 19, 4], 'material':
                                        'Dirt'}, {'xyz': [40, 19, 4], 'material':
                                                            'Dirt'}, {'xyz': [41, 19, 4], 'material':
                                                                                'Dirt'}, {'xyz': [42, 19, 4], 'material':
                                                                                                    'Dirt'}, {'xyz': [43, 19, 4], 'material': 'Dirt'},
                                      {'xyz': [44, 19, 4], 'material':
                                        'Dirt'}, {'xyz': [45, 19, 4], 'material':
                                                            'Dirt'}, {'xyz': [46, 19, 4], 'material':
                                                                                'Dirt'}, {'xyz': [19, 20, 4], 'material':
                                                                                                    'Dirt'}, {'xyz': [28, 20, 4], 'material': 'Dirt'},
                                      {'xyz': [37, 20, 4], 'material':
                                        'Dirt'}, {'xyz': [46, 20, 4], 'material':
                                                            'Dirt'}, {'xyz': [19, 21, 4], 'material':
                                                                                'Dirt'}, {'xyz': [28, 21, 4], 'material':
                                                                                                    'Dirt'}, {'xyz': [37, 21, 4], 'material': 'Dirt'},
                                      {'xyz': [46, 21, 4], 'material':
                                        'Dirt'}, {'xyz': [19, 22, 4], 'material':
                                                            'Dirt'}, {'xyz': [28, 22, 4], 'material':
                                                                                'Dirt'}, {'xyz': [37, 22, 4], 'material':
                                                                                                    'Dirt'}, {'xyz': [46, 22, 4], 'material': 'Dirt'},
                                      {'xyz': [19, 23, 4], 'material':
                                        'Dirt'}, {'xyz': [28, 23, 4], 'material':
                                                            'Dirt'}, {'xyz': [37, 23, 4], 'material':
                                                                                'Dirt'}, {'xyz': [46, 23, 4], 'material':
                                                                                                    'Dirt'}, {'xyz': [19, 24, 4], 'material': 'Dirt'},
                                      {'xyz': [28, 24, 4], 'material':
                                        'Dirt'}, {'xyz': [37, 24, 4], 'material':
                                                            'Dirt'}, {'xyz': [46, 24, 4], 'material':
                                                                                'Dirt'}, {'xyz': [19, 25, 4], 'material':
                                                                                                    'Dirt'}, {'xyz': [28, 25, 4], 'material': 'Dirt'},
                                      {'xyz': [37, 25, 4], 'material':
                                        'Dirt'}, {'xyz': [46, 25, 4], 'material':
                                                            'Dirt'}, {'xyz': [19, 26, 4], 'material':
                                                                                'Dirt'}, {'xyz': [28, 26, 4], 'material': 'Dirt'
                                                                                                    }, {'xyz': [37, 26, 4], 'material': 'Dirt'
                                                                                                            }, {'xyz': [46, 26, 4], 'material': 'Dirt'}, {
                                                                                                                    'xyz': [19, 27, 4], 'material': 'Dirt'
                                                                                                            }, {'xyz': [28, 27, 4], 'material': 'Dirt'}, {
                                                                                                                    'xyz': [37, 27, 4], 'material': 'Dirt'
                                                                                                            }, {'xyz': [46, 27, 4], 'material': 'Dirt'}, {
                                                                                                                    'xyz': [19, 28, 4], 'material': 'Dirt'
                                                                                                            }, {'xyz': [20, 28, 4], 'material': 'Dirt'}, {
                                                                                                                    'xyz': [21, 28, 4], 'material': 'Dirt'
                                                                                                            }, {'xyz': [22, 28, 4], 'material': 'Dirt'}, {
                                                                                                                    'xyz': [23, 28, 4], 'material': 'Dirt'
                                                                                                            }, {'xyz': [24, 28, 4], 'material': 'Dirt'}, {
                                                                                                                    'xyz': [25, 28, 4], 'material': 'Dirt'
                                                                                                            }, {'xyz': [26, 28, 4], 'material': 'Dirt'}, {
                                                                                                                    'xyz': [27, 28, 4], 'material': 'Dirt'
                                                                                                            }, {'xyz': [28, 28, 4], 'material': 'Dirt'}, {
                                                                                                                    'xyz': [29, 28, 4], 'material': 'Dirt'
                                                                                                            }, {'xyz': [30, 28, 4], 'material': 'Dirt'}, {
                                                                                                                    'xyz': [31, 28, 4], 'material': 'Dirt'
                                                                                                            }, {'xyz': [32, 28, 4], 'material': 'Dirt'}, {
                                                                                                                    'xyz': [33, 28, 4], 'material': 'Dirt'
                                                                                                            }, {'xyz': [34, 28, 4], 'material': 'Dirt'}, {
                                                                                                                    'xyz': [35, 28, 4], 'material': 'Dirt'
                                                                                                            }, {'xyz': [36, 28, 4], 'material': 'Dirt'}, {
                                                                                                                    'xyz': [37, 28, 4], 'material': 'Dirt'
                                                                                                            }, {'xyz': [38, 28, 4], 'material': 'Dirt'}, {
                                                                                                                    'xyz': [39, 28, 4], 'material': 'Dirt'
                                                                                                            }, {'xyz': [40, 28, 4], 'material': 'Dirt'}, {
                                                                                                                    'xyz': [41, 28, 4], 'material': 'Dirt'
                                                                                                            }, {'xyz': [42, 28, 4], 'material': 'Dirt'}, {
                                                                                                                    'xyz': [43, 28, 4], 'material': 'Dirt'
                                                                                                            }, {'xyz': [44, 28, 4], 'material': 'Dirt'}, {
                                                                                                                    'xyz': [45, 28, 4], 'material': 'Dirt'
                                                                                                            }, {'xyz': [46, 28, 4], 'material': 'Dirt'}, {
                                                                                                                    'xyz': [19, 19, 5], 'material': 'Dirt'
                                                                                                            }, {'xyz': [20, 19, 5], 'material': 'Dirt'}, {
                                                                                                                    'xyz': [21, 19, 5], 'material': 'Dirt'
                                                                                                            }, {'xyz': [22, 19, 5], 'material': 'Dirt'}, {
                                                                                                                    'xyz': [23, 19, 5], 'material': 'Dirt'
                                                                                                            }, {'xyz': [24, 19, 5], 'material': 'Dirt'}, {
                                                                                                                    'xyz': [25, 19, 5], 'material': 'Dirt'
                                                                                                            }, {'xyz': [26, 19, 5], 'material': 'Dirt'}, {
                                                                                                                    'xyz': [27, 19, 5], 'material': 'Dirt'
                                                                                                            }, {'xyz': [28, 19, 5], 'material': 'Dirt'}, {
                                                                                                                    'xyz': [29, 19, 5], 'material': 'Dirt'
                                                                                                            }, {'xyz': [30, 19, 5], 'material': 'Dirt'}, {
                                                                                                                    'xyz': [31, 19, 5], 'material': 'Dirt'
                                                                                                            }, {'xyz': [32, 19, 5], 'material': 'Dirt'}, {
                                                                                                                    'xyz': [33, 19, 5], 'material': 'Dirt'
                                                                                                            }, {'xyz': [34, 19, 5], 'material': 'Dirt'}, {
                                                                                                                    'xyz': [35, 19, 5], 'material': 'Dirt'
                                                                                                            }, {'xyz': [36, 19, 5], 'material': 'Dirt'}, {
                                                                                                                    'xyz': [37, 19, 5], 'material': 'Dirt'
                                                                                                            }, {'xyz': [19, 20, 5], 'material': 'Dirt'}, {
                                                                                                                    'xyz': [28, 20, 5], 'material': 'Dirt'
                                                                                                            }, {'xyz': [37, 20, 5], 'material': 'Dirt'}, {
                                                                                                                    'xyz': [19, 21, 5], 'material': 'Dirt'
                                                                                                            }, {'xyz': [28, 21, 5], 'material': 'Dirt'}, {
                                                                                                                    'xyz': [37, 21, 5], 'material': 'Dirt'
                                                                                                            }, {'xyz': [19, 22, 5], 'material': 'Dirt'}, {
                                                                                                                    'xyz': [28, 22, 5], 'material': 'Dirt'
                                                                                                            }, {'xyz': [37, 22, 5], 'material': 'Dirt'}, {
                                                                                                                    'xyz': [19, 23, 5], 'material': 'Dirt'
                                                                                                            }, {'xyz': [28, 23, 5], 'material': 'Dirt'}, {
                                                                                                                    'xyz': [37, 23, 5], 'material': 'Dirt'
                                                                                                            }, {'xyz': [19, 24, 5], 'material': 'Dirt'}, {
                                                                                                                    'xyz': [28, 24, 5], 'material': 'Dirt'
                                                                                                            }, {'xyz': [19, 25, 5], 'material': 'Dirt'}, {
                                                                                                                    'xyz': [28, 25, 5], 'material': 'Dirt'
                                                                                                            }, {'xyz': [19, 26, 5], 'material': 'Dirt'}, {
                                                                                                                    'xyz': [28, 26, 5], 'material': 'Dirt'
                                                                                                            }, {'xyz': [37, 26, 5], 'material': 'Dirt'}, {
                                                                                                                    'xyz': [19, 27, 5], 'material': 'Dirt'
                                                                                                            }, {'xyz': [28, 27, 5], 'material': 'Dirt'}, {
                                                                                                                    'xyz': [37, 27, 5], 'material': 'Dirt'
                                                                                                            }, {'xyz': [19, 28, 5], 'material': 'Dirt'}, {
                                                                                                                    'xyz': [20, 28, 5], 'material': 'Dirt'
                                                                                                            }, {'xyz': [21, 28, 5], 'material': 'Dirt'}, {
                                                                                                                    'xyz': [22, 28, 5], 'material': 'Dirt'
                                                                                                            }, {'xyz': [23, 28, 5], 'material': 'Dirt'}, {
                                                                                                                    'xyz': [24, 28, 5], 'material': 'Dirt'
                                                                                                            }, {'xyz': [25, 28, 5], 'material': 'Dirt'}, {
                                                                                                                    'xyz': [26, 28, 5], 'material': 'Dirt'
                                                                                                            }, {'xyz': [27, 28, 5], 'material': 'Dirt'}, {
                                                                                                                    'xyz': [28, 28, 5], 'material': 'Dirt'
                                                                                                            }, {'xyz': [29, 28, 5], 'material': 'Dirt'}, {
                                                                                                                    'xyz': [30, 28, 5], 'material': 'Dirt'
                                                                                                            }, {'xyz': [31, 28, 5], 'material': 'Dirt'}, {
                                                                                                                    'xyz': [32, 28, 5], 'material': 'Dirt'
                                                                                                            }, {'xyz': [33, 28, 5], 'material': 'Dirt'}, {
                                                                                                                    'xyz': [34, 28, 5], 'material': 'Dirt'
                                                                                                            }, {'xyz': [35, 28, 5], 'material': 'Dirt'}, {
                                                                                                                    'xyz': [36, 28, 5], 'material': 'Dirt'
                                                                                                            }, {'xyz': [37, 28, 5], 'material': 'Dirt'}, {
                                                                                                                    'xyz': [19, 19, 6], 'material': 'Dirt'
                                                                                                            }, {'xyz': [20, 19, 6], 'material': 'Dirt'}, {
                                                                                                                    'xyz': [21, 19, 6], 'material': 'Dirt'
                                                                                                            }, {'xyz': [22, 19, 6], 'material': 'Dirt'}, {
                                                                                                                    'xyz': [23, 19, 6], 'material': 'Dirt'
                                                                                                            }, {'xyz': [24, 19, 6], 'material': 'Dirt'}, {
                                                                                                                    'xyz': [25, 19, 6], 'material': 'Dirt'
                                                                                                            }, {'xyz': [26, 19, 6], 'material': 'Dirt'}, {
                                                                                                                    'xyz': [27, 19, 6], 'material': 'Dirt'
                                                                                                            }, {'xyz': [28, 19, 6], 'material': 'Dirt'}, {
                                                                                                                    'xyz': [19, 20, 6], 'material': 'Dirt'
                                                                                                            }, {'xyz': [28, 20, 6], 'material': 'Dirt'}, {
                                                                                                                    'xyz': [19, 21, 6], 'material': 'Dirt'
                                                                                                            }, {'xyz': [28, 21, 6], 'material': 'Dirt'}, {
                                                                                                                    'xyz': [19, 22, 6], 'material': 'Dirt'
                                                                                                            }, {'xyz': [28, 22, 6], 'material': 'Dirt'}, {
                                                                                                                    'xyz': [19, 23, 6], 'material': 'Dirt'
                                                                                                            }, {'xyz': [28, 23, 6], 'material': 'Dirt'}, {
                                                                                                                    'xyz': [19, 24, 6], 'material': 'Dirt'
                                                                                                            }, {'xyz': [19, 25, 6], 'material': 'Dirt'}, {
                                                                                                                    'xyz': [19, 26, 6], 'material': 'Dirt'
                                                                                                            }, {'xyz': [28, 26, 6], 'material': 'Dirt'}, {
                                                                                                                    'xyz': [19, 27, 6], 'material': 'Dirt'
                                                                                                            }, {'xyz': [28, 27, 6], 'material': 'Dirt'}, {
                                                                                                                    'xyz': [19, 28, 6], 'material': 'Dirt'
                                                                                                            }, {'xyz': [20, 28, 6], 'material': 'Dirt'}, {
                                                                                                                    'xyz': [21, 28, 6], 'material': 'Dirt'
                                                                                                            }, {'xyz': [22, 28, 6], 'material': 'Dirt'}, {
                                                                                                                    'xyz': [23, 28, 6], 'material': 'Dirt'
                                                                                                            }, {'xyz': [24, 28, 6], 'material': 'Dirt'}, {
                                                                                                                    'xyz': [25, 28, 6], 'material': 'Dirt'
                                                                                                            }, {'xyz': [26, 28, 6], 'material': 'Dirt'}, {
                                                                                                                    'xyz': [27, 28, 6], 'material': 'Dirt'
                                                                                                            }, {'xyz': [28, 28, 6], 'material': 'Dirt'}]
        }, ""

    if subPass == 5:
        return {
                'reasoning':
                'Create a sealed cistern under the rainfall point: excavate the interior down to z=1 (leave z=0 as dirt so water cannot touch the world bottom and be lost), and build a 1-voxel-thick perimeter wall up to z=7 to stop lateral runoff to the map edges. With thousands of rain voxels, the cistern will fill to at least z=7, giving a water depth of 6+ voxels (from z=1 up).',
                'voxels':
                [{'xyz': [26, 26, 1], 'material': 'Air'}, {'xyz': [27, 26, 1], 'material':
                                                                                                      'Air'}, {'xyz': [28, 26, 1], 'material': 'Air'},
                  {'xyz': [29, 26, 1], 'material': 'Air'}, {'xyz': [30, 26, 1], 'material':
                                                                                                      'Air'}, {'xyz': [31, 26, 1], 'material': 'Air'},
                  {'xyz': [26, 27, 1], 'material':
                    'Air'}, {'xyz': [27, 27, 1], 'material':
                                      'Air'}, {'xyz': [28, 27, 1], 'material':
                                                        'Air'}, {'xyz': [29, 27, 1], 'material':
                                                                          'Air'}, {'xyz': [30, 27, 1], 'material':
                                                                                            'Air'}, {'xyz': [31, 27, 1], 'material': 'Air'},
                  {'xyz': [26, 28, 1], 'material':
                    'Air'}, {'xyz': [27, 28, 1], 'material':
                                      'Air'}, {'xyz': [28, 28, 1], 'material':
                                                        'Air'}, {'xyz': [29, 28, 1], 'material':
                                                                          'Air'}, {'xyz': [30, 28, 1], 'material':
                                                                                            'Air'}, {'xyz': [31, 28, 1], 'material': 'Air'},
                  {'xyz': [26, 29, 1], 'material':
                    'Air'}, {'xyz': [27, 29, 1], 'material':
                                      'Air'}, {'xyz': [28, 29, 1], 'material':
                                                        'Air'}, {'xyz': [29, 29, 1], 'material':
                                                                          'Air'}, {'xyz': [30, 29, 1], 'material':
                                                                                            'Air'}, {'xyz': [31, 29, 1], 'material': 'Air'},
                  {'xyz': [26, 30, 1], 'material':
                    'Air'}, {'xyz': [27, 30, 1], 'material':
                                      'Air'}, {'xyz': [28, 30, 1], 'material':
                                                        'Air'}, {'xyz': [29, 30, 1], 'material':
                                                                          'Air'}, {'xyz': [30, 30, 1], 'material':
                                                                                            'Air'}, {'xyz': [31, 30, 1], 'material': 'Air'},
                  {'xyz': [26, 31, 1], 'material':
                    'Air'}, {'xyz': [27, 31, 1], 'material':
                                      'Air'}, {'xyz': [28, 31, 1], 'material':
                                                        'Air'}, {'xyz': [29, 31, 1], 'material':
                                                                          'Air'}, {'xyz': [30, 31, 1], 'material':
                                                                                            'Air'}, {'xyz': [31, 31, 1], 'material': 'Air'},
                  {'xyz': [26, 26, 2], 'material':
                    'Air'}, {'xyz': [27, 26, 2], 'material':
                                      'Air'}, {'xyz': [28, 26, 2], 'material':
                                                        'Air'}, {'xyz': [29, 26, 2], 'material':
                                                                          'Air'}, {'xyz': [30, 26, 2], 'material':
                                                                                            'Air'}, {'xyz': [31, 26, 2], 'material': 'Air'},
                  {'xyz': [26, 27, 2], 'material':
                    'Air'}, {'xyz': [27, 27, 2], 'material':
                                      'Air'}, {'xyz': [28, 27, 2], 'material':
                                                        'Air'}, {'xyz': [29, 27, 2], 'material':
                                                                          'Air'}, {'xyz': [30, 27, 2], 'material':
                                                                                            'Air'}, {'xyz': [31, 27, 2], 'material': 'Air'},
                  {'xyz': [26, 28, 2], 'material':
                    'Air'}, {'xyz': [27, 28, 2], 'material':
                                      'Air'}, {'xyz': [28, 28, 2], 'material':
                                                        'Air'}, {'xyz': [29, 28, 2], 'material':
                                                                          'Air'}, {'xyz': [30, 28, 2], 'material':
                                                                                            'Air'}, {'xyz': [31, 28, 2], 'material': 'Air'},
                  {'xyz': [26, 29, 2], 'material':
                    'Air'}, {'xyz': [27, 29, 2], 'material':
                                      'Air'}, {'xyz': [28, 29, 2], 'material':
                                                        'Air'}, {'xyz': [29, 29, 2], 'material':
                                                                          'Air'}, {'xyz': [30, 29, 2], 'material':
                                                                                            'Air'}, {'xyz': [31, 29, 2], 'material': 'Air'
                                                                                                              }, {'xyz': [26, 30, 2], 'material': 'Air'},
                  {'xyz': [27, 30, 2], 'material':
                    'Air'}, {'xyz': [28, 30, 2], 'material':
                                      'Air'}, {'xyz': [29, 30, 2], 'material':
                                                        'Air'}, {'xyz': [30, 30, 2], 'material':
                                                                          'Air'}, {'xyz': [31, 30, 2], 'material':
                                                                                            'Air'}, {'xyz': [26, 31, 2], 'material': 'Air'
                                                                                                              }, {'xyz': [27, 31, 2], 'material': 'Air'},
                  {'xyz': [28, 31, 2], 'material':
                    'Air'}, {'xyz': [29, 31, 2], 'material':
                                      'Air'}, {'xyz': [30, 31, 2], 'material':
                                                        'Air'}, {'xyz': [31, 31, 2], 'material':
                                                                          'Air'}, {'xyz': [25, 25, 3], 'material':
                                                                                            'Dirt'}, {'xyz': [26, 25, 3], 'material': 'Dirt'
                                                                                                                }, {'xyz': [27, 25, 3], 'material': 'Dirt'},
                  {'xyz': [28, 25, 3], 'material':
                    'Dirt'}, {'xyz': [29, 25, 3], 'material':
                                        'Dirt'}, {'xyz': [30, 25, 3], 'material':
                                                            'Dirt'}, {'xyz': [31, 25, 3], 'material':
                                                                                'Dirt'}, {'xyz': [32, 25, 3], 'material':
                                                                                                    'Dirt'}, {'xyz': [25, 26, 3], 'material': 'Dirt'},
                  {'xyz': [32, 26, 3], 'material':
                    'Dirt'}, {'xyz': [25, 27, 3], 'material':
                                        'Dirt'}, {'xyz': [32, 27, 3], 'material':
                                                            'Dirt'}, {'xyz': [25, 28, 3], 'material':
                                                                                'Dirt'}, {'xyz': [32, 28, 3], 'material':
                                                                                                    'Dirt'}, {'xyz': [25, 29, 3], 'material': 'Dirt'},
                  {'xyz': [32, 29, 3], 'material':
                    'Dirt'}, {'xyz': [25, 30, 3], 'material':
                                        'Dirt'}, {'xyz': [32, 30, 3], 'material':
                                                            'Dirt'}, {'xyz': [25, 31, 3], 'material':
                                                                                'Dirt'}, {'xyz': [32, 31, 3], 'material':
                                                                                                    'Dirt'}, {'xyz': [25, 32, 3], 'material': 'Dirt'},
                  {'xyz': [26, 32, 3], 'material':
                    'Dirt'}, {'xyz': [27, 32, 3], 'material':
                                        'Dirt'}, {'xyz': [28, 32, 3], 'material':
                                                            'Dirt'}, {'xyz': [29, 32, 3], 'material':
                                                                                'Dirt'}, {'xyz': [30, 32, 3], 'material':
                                                                                                    'Dirt'}, {'xyz': [31, 32, 3], 'material': 'Dirt'},
                  {'xyz': [32, 32, 3], 'material':
                    'Dirt'}, {'xyz': [25, 25, 4], 'material':
                                        'Dirt'}, {'xyz': [26, 25, 4], 'material':
                                                            'Dirt'}, {'xyz': [27, 25, 4], 'material':
                                                                                'Dirt'}, {'xyz': [28, 25, 4], 'material':
                                                                                                    'Dirt'}, {'xyz': [29, 25, 4], 'material': 'Dirt'},
                  {'xyz': [30, 25, 4], 'material':
                    'Dirt'}, {'xyz': [31, 25, 4], 'material':
                                        'Dirt'}, {'xyz': [32, 25, 4], 'material':
                                                            'Dirt'}, {'xyz': [25, 26, 4], 'material':
                                                                                'Dirt'}, {'xyz': [32, 26, 4], 'material':
                                                                                                    'Dirt'}, {'xyz': [25, 27, 4], 'material': 'Dirt'},
                  {'xyz': [32, 27, 4], 'material':
                    'Dirt'}, {'xyz': [25, 28, 4], 'material':
                                        'Dirt'}, {'xyz': [32, 28, 4], 'material':
                                                            'Dirt'}, {'xyz': [25, 29, 4], 'material':
                                                                                'Dirt'}, {'xyz': [32, 29, 4], 'material':
                                                                                                    'Dirt'}, {'xyz': [25, 30, 4], 'material': 'Dirt'},
                  {'xyz': [32, 30, 4], 'material':
                    'Dirt'}, {'xyz': [25, 31, 4], 'material':
                                        'Dirt'}, {'xyz': [32, 31, 4], 'material':
                                                            'Dirt'}, {'xyz': [25, 32, 4], 'material':
                                                                                'Dirt'}, {'xyz': [26, 32, 4], 'material':
                                                                                                    'Dirt'}, {'xyz': [27, 32, 4], 'material': 'Dirt'},
                  {'xyz': [28, 32, 4], 'material':
                    'Dirt'}, {'xyz': [29, 32, 4], 'material':
                                        'Dirt'}, {'xyz': [30, 32, 4], 'material':
                                                            'Dirt'}, {'xyz': [31, 32, 4], 'material':
                                                                                'Dirt'}, {'xyz': [32, 32, 4], 'material':
                                                                                                    'Dirt'}, {'xyz': [25, 25, 5], 'material': 'Dirt'},
                  {'xyz': [26, 25, 5], 'material':
                    'Dirt'}, {'xyz': [27, 25, 5], 'material':
                                        'Dirt'}, {'xyz': [28, 25, 5], 'material':
                                                            'Dirt'}, {'xyz': [29, 25, 5], 'material':
                                                                                'Dirt'}, {'xyz': [30, 25, 5], 'material':
                                                                                                    'Dirt'}, {'xyz': [31, 25, 5], 'material': 'Dirt'},
                  {'xyz': [32, 25, 5], 'material':
                    'Dirt'}, {'xyz': [25, 26, 5], 'material':
                                        'Dirt'}, {'xyz': [32, 26, 5], 'material':
                                                            'Dirt'}, {'xyz': [25, 27, 5], 'material':
                                                                                'Dirt'}, {'xyz': [32, 27, 5], 'material':
                                                                                                    'Dirt'}, {'xyz': [25, 28, 5], 'material': 'Dirt'},
                  {'xyz': [32, 28, 5], 'material':
                    'Dirt'}, {'xyz': [25, 29, 5], 'material':
                                        'Dirt'}, {'xyz': [32, 29, 5], 'material':
                                                            'Dirt'}, {'xyz': [25, 30, 5], 'material':
                                                                                'Dirt'}, {'xyz': [32, 30, 5], 'material':
                                                                                                    'Dirt'}, {'xyz': [25, 31, 5], 'material': 'Dirt'},
                  {'xyz': [32, 31, 5], 'material':
                    'Dirt'}, {'xyz': [25, 32, 5], 'material':
                                        'Dirt'}, {'xyz': [26, 32, 5], 'material':
                                                            'Dirt'}, {'xyz': [27, 32, 5], 'material':
                                                                                'Dirt'}, {'xyz': [28, 32, 5], 'material':
                                                                                                    'Dirt'}, {'xyz': [29, 32, 5], 'material': 'Dirt'},
                  {'xyz': [30, 32, 5], 'material':
                    'Dirt'}, {'xyz': [31, 32, 5], 'material':
                                        'Dirt'}, {'xyz': [32, 32, 5], 'material':
                                                            'Dirt'}, {'xyz': [25, 25, 6], 'material':
                                                                                'Dirt'}, {'xyz': [26, 25, 6], 'material':
                                                                                                    'Dirt'}, {'xyz': [27, 25, 6], 'material': 'Dirt'},
                  {'xyz': [28, 25, 6], 'material':
                    'Dirt'}, {'xyz': [29, 25, 6], 'material':
                                        'Dirt'}, {'xyz': [30, 25, 6], 'material':
                                                            'Dirt'}, {'xyz': [31, 25, 6], 'material':
                                                                                'Dirt'}, {'xyz': [32, 25, 6], 'material':
                                                                                                    'Dirt'}, {'xyz': [25, 26, 6], 'material': 'Dirt'},
                  {'xyz': [32, 26, 6], 'material':
                    'Dirt'}, {'xyz': [25, 27, 6], 'material':
                                        'Dirt'}, {'xyz': [32, 27, 6], 'material':
                                                            'Dirt'}, {'xyz': [25, 28, 6], 'material':
                                                                                'Dirt'}, {'xyz': [32, 28, 6], 'material':
                                                                                                    'Dirt'}, {'xyz': [25, 29, 6], 'material': 'Dirt'},
                  {'xyz': [32, 29, 6], 'material':
                    'Dirt'}, {'xyz': [25, 30, 6], 'material':
                                        'Dirt'}, {'xyz': [32, 30, 6], 'material':
                                                            'Dirt'}, {'xyz': [25, 31, 6], 'material':
                                                                                'Dirt'}, {'xyz': [32, 31, 6], 'material':
                                                                                                    'Dirt'}, {'xyz': [25, 32, 6], 'material': 'Dirt'},
                  {'xyz': [26, 32, 6], 'material':
                    'Dirt'}, {'xyz': [27, 32, 6], 'material':
                                        'Dirt'}, {'xyz': [28, 32, 6], 'material':
                                                            'Dirt'}, {'xyz': [29, 32, 6], 'material':
                                                                                'Dirt'}, {'xyz': [30, 32, 6], 'material':
                                                                                                    'Dirt'}, {'xyz': [31, 32, 6], 'material': 'Dirt'},
                  {'xyz': [32, 32, 6], 'material':
                    'Dirt'}, {'xyz': [25, 25, 7], 'material':
                                        'Dirt'}, {'xyz': [26, 25, 7], 'material': 'Dirt'}, {
                                                'xyz':
                                                [27, 25,
                                                  7], 'material': 'Dirt'
                                        }, {'xyz': [28, 25, 7], 'material':
                                                'Dirt'}, {'xyz': [29, 25, 7], 'material':
                                                                    'Dirt'}, {'xyz': [30, 25, 7], 'material':
                                                                                        'Dirt'}, {'xyz': [31, 25, 7], 'material': 'Dirt'}, {
                                                                                                'xyz':
                                                                                                [32, 25,
                                                                                                  7], 'material': 'Dirt'
                                                                                        }, {'xyz': [25, 26, 7], 'material':
                                                                                                'Dirt'}, {'xyz': [32, 26, 7], 'material': 'Dirt'}, {
                                                                                                        'xyz': [25, 27,
                                                                                                                        7], 'material': 'Dirt'
                                                                                                }, {'xyz': [32, 27, 7], 'material': 'Dirt'
                                                                                                        }, {'xyz': [25, 28, 7], 'material': 'Dirt'
                                                                                                                }, {'xyz': [32, 28, 7], 'material': 'Dirt'},
                  {'xyz': [25, 29, 7], 'material':
                    'Dirt'}, {'xyz': [32, 29, 7], 'material':
                                        'Dirt'}, {'xyz': [25, 30, 7], 'material': 'Dirt'
                                                            }, {'xyz': [32, 30, 7], 'material': 'Dirt'
                                                                    }, {'xyz': [25, 31, 7], 'material': 'Dirt'
                                                                            }, {'xyz': [32, 31, 7], 'material': 'Dirt'
                                                                                    }, {'xyz': [25, 32, 7], 'material': 'Dirt'
                                                                                            }, {'xyz': [26, 32, 7], 'material': 'Dirt'
                                                                                                    }, {'xyz': [27, 32, 7], 'material': 'Dirt'
                                                                                                            }, {'xyz': [28, 32, 7], 'material': 'Dirt'}, {
                                                                                                                    'xyz': [29, 32, 7], 'material': 'Dirt'
                                                                                                            }, {'xyz': [30, 32, 7], 'material': 'Dirt'}, {
                                                                                                                    'xyz': [31, 32, 7], 'material': 'Dirt'
                                                                                                            }, {'xyz': [32, 32, 7], 'material': 'Dirt'}]
        }, ""

    if subPass == 6:
        return {
                'reasoning':
                'Excavate two separate rectangular basins (open to the sky) by removing dirt at z=2 and z=1, leaving the z=0 dirt layer intact as an impermeable floor. Each basin is 11x10x2 = 220 voxels of capacity, so after thousands of rainfall voxels they will fill and remain as two distinct lakes (>200 voxels each), while any excess surface water can still run off the map edges.',
                'voxels':
                [{'xyz': [18, 27, 1], 'material': 'Air'}, {'xyz': [18, 27, 2], 'material':
                                                                                                      'Air'}, {'xyz': [18, 28, 1], 'material': 'Air'},
                  {'xyz': [18, 28, 2], 'material': 'Air'}, {'xyz': [18, 29, 1], 'material':
                                                                                                      'Air'}, {'xyz': [18, 29, 2], 'material': 'Air'},
                  {'xyz': [18, 30, 1], 'material':
                    'Air'}, {'xyz': [18, 30, 2], 'material':
                                      'Air'}, {'xyz': [18, 31, 1], 'material':
                                                        'Air'}, {'xyz': [18, 31, 2], 'material':
                                                                          'Air'}, {'xyz': [18, 32, 1], 'material':
                                                                                            'Air'}, {'xyz': [18, 32, 2], 'material': 'Air'},
                  {'xyz': [18, 33, 1], 'material':
                    'Air'}, {'xyz': [18, 33, 2], 'material':
                                      'Air'}, {'xyz': [18, 34, 1], 'material':
                                                        'Air'}, {'xyz': [18, 34, 2], 'material':
                                                                          'Air'}, {'xyz': [18, 35, 1], 'material':
                                                                                            'Air'}, {'xyz': [18, 35, 2], 'material': 'Air'},
                  {'xyz': [18, 36, 1], 'material':
                    'Air'}, {'xyz': [18, 36, 2], 'material':
                                      'Air'}, {'xyz': [19, 27, 1], 'material':
                                                        'Air'}, {'xyz': [19, 27, 2], 'material':
                                                                          'Air'}, {'xyz': [19, 28, 1], 'material':
                                                                                            'Air'}, {'xyz': [19, 28, 2], 'material': 'Air'},
                  {'xyz': [19, 29, 1], 'material':
                    'Air'}, {'xyz': [19, 29, 2], 'material':
                                      'Air'}, {'xyz': [19, 30, 1], 'material':
                                                        'Air'}, {'xyz': [19, 30, 2], 'material':
                                                                          'Air'}, {'xyz': [19, 31, 1], 'material':
                                                                                            'Air'}, {'xyz': [19, 31, 2], 'material': 'Air'},
                  {'xyz': [19, 32, 1], 'material':
                    'Air'}, {'xyz': [19, 32, 2], 'material':
                                      'Air'}, {'xyz': [19, 33, 1], 'material':
                                                        'Air'}, {'xyz': [19, 33, 2], 'material':
                                                                          'Air'}, {'xyz': [19, 34, 1], 'material':
                                                                                            'Air'}, {'xyz': [19, 34, 2], 'material': 'Air'},
                  {'xyz': [19, 35, 1], 'material':
                    'Air'}, {'xyz': [19, 35, 2], 'material':
                                      'Air'}, {'xyz': [19, 36, 1], 'material':
                                                        'Air'}, {'xyz': [19, 36, 2], 'material':
                                                                          'Air'}, {'xyz': [20, 27, 1], 'material':
                                                                                            'Air'}, {'xyz': [20, 27, 2], 'material': 'Air'},
                  {'xyz': [20, 28, 1], 'material':
                    'Air'}, {'xyz': [20, 28, 2], 'material':
                                      'Air'}, {'xyz': [20, 29, 1], 'material':
                                                        'Air'}, {'xyz': [20, 29, 2], 'material':
                                                                          'Air'}, {'xyz': [20, 30, 1], 'material':
                                                                                            'Air'}, {'xyz': [20, 30, 2], 'material': 'Air'},
                  {'xyz': [20, 31, 1], 'material':
                    'Air'}, {'xyz': [20, 31, 2], 'material':
                                      'Air'}, {'xyz': [20, 32, 1], 'material':
                                                        'Air'}, {'xyz': [20, 32, 2], 'material':
                                                                          'Air'}, {'xyz': [20, 33, 1], 'material':
                                                                                            'Air'}, {'xyz': [20, 33, 2], 'material': 'Air'},
                  {'xyz': [20, 34, 1], 'material':
                    'Air'}, {'xyz': [20, 34, 2], 'material':
                                      'Air'}, {'xyz': [20, 35, 1], 'material':
                                                        'Air'}, {'xyz': [20, 35, 2], 'material':
                                                                          'Air'}, {'xyz': [20, 36, 1], 'material':
                                                                                            'Air'}, {'xyz': [20, 36, 2], 'material': 'Air'},
                  {'xyz': [21, 27, 1], 'material':
                    'Air'}, {'xyz': [21, 27, 2], 'material':
                                      'Air'}, {'xyz': [21, 28, 1], 'material':
                                                        'Air'}, {'xyz': [21, 28, 2], 'material':
                                                                          'Air'}, {'xyz': [21, 29, 1], 'material':
                                                                                            'Air'}, {'xyz': [21, 29, 2], 'material': 'Air'},
                  {'xyz': [21, 30, 1], 'material':
                    'Air'}, {'xyz': [21, 30, 2], 'material':
                                      'Air'}, {'xyz': [21, 31, 1], 'material':
                                                        'Air'}, {'xyz': [21, 31, 2], 'material':
                                                                          'Air'}, {'xyz': [21, 32, 1], 'material':
                                                                                            'Air'}, {'xyz': [21, 32, 2], 'material': 'Air'},
                  {'xyz': [21, 33, 1], 'material':
                    'Air'}, {'xyz': [21, 33, 2], 'material':
                                      'Air'}, {'xyz': [21, 34, 1], 'material':
                                                        'Air'}, {'xyz': [21, 34, 2], 'material':
                                                                          'Air'}, {'xyz': [21, 35, 1], 'material':
                                                                                            'Air'}, {'xyz': [21, 35, 2], 'material': 'Air'},
                  {'xyz': [21, 36, 1], 'material':
                    'Air'}, {'xyz': [21, 36, 2], 'material':
                                      'Air'}, {'xyz': [22, 27, 1], 'material':
                                                        'Air'}, {'xyz': [22, 27, 2], 'material':
                                                                          'Air'}, {'xyz': [22, 28, 1], 'material':
                                                                                            'Air'}, {'xyz': [22, 28, 2], 'material': 'Air'},
                  {'xyz': [22, 29, 1], 'material':
                    'Air'}, {'xyz': [22, 29, 2], 'material':
                                      'Air'}, {'xyz': [22, 30, 1], 'material':
                                                        'Air'}, {'xyz': [22, 30, 2], 'material':
                                                                          'Air'}, {'xyz': [22, 31, 1], 'material':
                                                                                            'Air'}, {'xyz': [22, 31, 2], 'material': 'Air'
                                                                                                              }, {'xyz': [22, 32, 1], 'material': 'Air'},
                  {'xyz': [22, 32, 2], 'material':
                    'Air'}, {'xyz': [22, 33, 1], 'material':
                                      'Air'}, {'xyz': [22, 33, 2], 'material':
                                                        'Air'}, {'xyz': [22, 34, 1], 'material':
                                                                          'Air'}, {'xyz': [22, 34, 2], 'material':
                                                                                            'Air'}, {'xyz': [22, 35, 1], 'material': 'Air'
                                                                                                              }, {'xyz': [22, 35, 2], 'material': 'Air'},
                  {'xyz': [22, 36, 1], 'material':
                    'Air'}, {'xyz': [22, 36, 2], 'material':
                                      'Air'}, {'xyz': [23, 27, 1], 'material':
                                                        'Air'}, {'xyz': [23, 27, 2], 'material':
                                                                          'Air'}, {'xyz': [23, 28, 1], 'material':
                                                                                            'Air'}, {'xyz': [23, 28, 2], 'material': 'Air'
                                                                                                              }, {'xyz': [23, 29, 1], 'material': 'Air'},
                  {'xyz': [23, 29, 2], 'material':
                    'Air'}, {'xyz': [23, 30, 1], 'material':
                                      'Air'}, {'xyz': [23, 30, 2], 'material':
                                                        'Air'}, {'xyz': [23, 31, 1], 'material':
                                                                          'Air'}, {'xyz': [23, 31, 2], 'material':
                                                                                            'Air'}, {'xyz': [23, 32, 1], 'material': 'Air'
                                                                                                              }, {'xyz': [23, 32, 2], 'material': 'Air'},
                  {'xyz': [23, 33, 1], 'material':
                    'Air'}, {'xyz': [23, 33, 2], 'material':
                                      'Air'}, {'xyz': [23, 34, 1], 'material':
                                                        'Air'}, {'xyz': [23, 34, 2], 'material':
                                                                          'Air'}, {'xyz': [23, 35, 1], 'material':
                                                                                            'Air'}, {'xyz': [23, 35, 2], 'material': 'Air'
                                                                                                              }, {'xyz': [23, 36, 1], 'material': 'Air'},
                  {'xyz': [23, 36, 2], 'material':
                    'Air'}, {'xyz': [24, 27, 1], 'material':
                                      'Air'}, {'xyz': [24, 27, 2], 'material':
                                                        'Air'}, {'xyz': [24, 28, 1], 'material':
                                                                          'Air'}, {'xyz': [24, 28, 2], 'material':
                                                                                            'Air'}, {'xyz': [24, 29, 1], 'material': 'Air'
                                                                                                              }, {'xyz': [24, 29, 2], 'material': 'Air'},
                  {'xyz': [24, 30, 1], 'material':
                    'Air'}, {'xyz': [24, 30, 2], 'material':
                                      'Air'}, {'xyz': [24, 31, 1], 'material':
                                                        'Air'}, {'xyz': [24, 31, 2], 'material':
                                                                          'Air'}, {'xyz': [24, 32, 1], 'material':
                                                                                            'Air'}, {'xyz': [24, 32, 2], 'material': 'Air'
                                                                                                              }, {'xyz': [24, 33, 1], 'material': 'Air'},
                  {'xyz': [24, 33, 2], 'material':
                    'Air'}, {'xyz': [24, 34, 1], 'material':
                                      'Air'}, {'xyz': [24, 34, 2], 'material':
                                                        'Air'}, {'xyz': [24, 35, 1], 'material':
                                                                          'Air'}, {'xyz': [24, 35, 2], 'material':
                                                                                            'Air'}, {'xyz': [24, 36, 1], 'material': 'Air'
                                                                                                              }, {'xyz': [24, 36, 2], 'material': 'Air'},
                  {'xyz': [25, 27, 1], 'material':
                    'Air'}, {'xyz': [25, 27, 2], 'material':
                                      'Air'}, {'xyz': [25, 28, 1], 'material':
                                                        'Air'}, {'xyz': [25, 28, 2], 'material':
                                                                          'Air'}, {'xyz': [25, 29, 1], 'material':
                                                                                            'Air'}, {'xyz': [25, 29, 2], 'material': 'Air'}, {
                                                                                                    'xyz': [25, 30,
                                                                                                                    1], 'material': 'Air'
                                                                                            }, {'xyz': [25, 30, 2], 'material':
                                                                                                    'Air'}, {'xyz': [25, 31, 1], 'material': 'Air'},
                  {'xyz': [25, 31, 2], 'material':
                    'Air'}, {'xyz': [25, 32, 1], 'material':
                                      'Air'}, {'xyz': [25, 32, 2], 'material':
                                                        'Air'}, {'xyz': [25, 33, 1], 'material':
                                                                          'Air'}, {'xyz': [25, 33, 2], 'material':
                                                                                            'Air'}, {'xyz': [25, 34, 1], 'material': 'Air'
                                                                                                              }, {'xyz': [25, 34, 2], 'material': 'Air'},
                  {'xyz': [25, 35, 1], 'material':
                    'Air'}, {'xyz': [25, 35, 2], 'material':
                                      'Air'}, {'xyz': [25, 36, 1], 'material':
                                                        'Air'}, {'xyz': [25, 36, 2], 'material':
                                                                          'Air'}, {'xyz': [26, 27, 1], 'material':
                                                                                            'Air'}, {'xyz': [26, 27, 2], 'material': 'Air'}, {
                                                                                                    'xyz': [26, 28,
                                                                                                                    1], 'material': 'Air'
                                                                                            }, {'xyz': [26, 28, 2], 'material':
                                                                                                    'Air'}, {'xyz': [26, 29, 1], 'material': 'Air'},
                  {'xyz': [26, 29, 2], 'material':
                    'Air'}, {'xyz': [26, 30, 1], 'material':
                                      'Air'}, {'xyz': [26, 30, 2], 'material':
                                                        'Air'}, {'xyz': [26, 31, 1], 'material':
                                                                          'Air'}, {'xyz': [26, 31, 2], 'material':
                                                                                            'Air'}, {'xyz': [26, 32, 1], 'material': 'Air'
                                                                                                              }, {'xyz': [26, 32, 2], 'material': 'Air'},
                  {'xyz': [26, 33, 1], 'material':
                    'Air'}, {'xyz': [26, 33, 2], 'material':
                                      'Air'}, {'xyz': [26, 34, 1], 'material':
                                                        'Air'}, {'xyz': [26, 34, 2], 'material':
                                                                          'Air'}, {'xyz': [26, 35, 1], 'material':
                                                                                            'Air'}, {'xyz': [26, 35, 2], 'material': 'Air'}, {
                                                                                                    'xyz': [26, 36,
                                                                                                                    1], 'material': 'Air'
                                                                                            }, {'xyz': [26, 36, 2], 'material':
                                                                                                    'Air'}, {'xyz': [27, 27, 1], 'material': 'Air'},
                  {'xyz': [27, 27, 2], 'material':
                    'Air'}, {'xyz': [27, 28, 1], 'material':
                                      'Air'}, {'xyz': [27, 28, 2], 'material':
                                                        'Air'}, {'xyz': [27, 29, 1], 'material':
                                                                          'Air'}, {'xyz': [27, 29, 2], 'material':
                                                                                            'Air'}, {'xyz': [27, 30, 1], 'material': 'Air'}, {
                                                                                                    'xyz': [27, 30,
                                                                                                                    2], 'material': 'Air'
                                                                                            }, {'xyz': [27, 31, 1], 'material':
                                                                                                    'Air'}, {'xyz': [27, 31, 2], 'material': 'Air'},
                  {'xyz': [27, 32, 1], 'material':
                    'Air'}, {'xyz': [27, 32, 2], 'material':
                                      'Air'}, {'xyz': [27, 33, 1], 'material':
                                                        'Air'}, {'xyz': [27, 33, 2], 'material':
                                                                          'Air'}, {'xyz': [27, 34, 1], 'material':
                                                                                            'Air'}, {'xyz': [27, 34, 2], 'material': 'Air'}, {
                                                                                                    'xyz': [27, 35,
                                                                                                                    1], 'material': 'Air'
                                                                                            }, {'xyz': [27, 35, 2], 'material':
                                                                                                    'Air'}, {'xyz': [27, 36, 1], 'material': 'Air'},
                  {'xyz': [27, 36, 2], 'material':
                    'Air'}, {'xyz': [28, 27, 1], 'material':
                                      'Air'}, {'xyz': [28, 27, 2], 'material':
                                                        'Air'}, {'xyz': [28, 28, 1], 'material':
                                                                          'Air'}, {'xyz': [28, 28, 2], 'material':
                                                                                            'Air'}, {'xyz': [28, 29, 1], 'material': 'Air'}, {
                                                                                                    'xyz': [28, 29,
                                                                                                                    2], 'material': 'Air'
                                                                                            }, {'xyz': [28, 30, 1], 'material':
                                                                                                    'Air'}, {'xyz': [28, 30, 2], 'material': 'Air'},
                  {'xyz': [28, 31, 1], 'material':
                    'Air'}, {'xyz': [28, 31, 2], 'material':
                                      'Air'}, {'xyz': [28, 32, 1], 'material':
                                                        'Air'}, {'xyz': [28, 32, 2], 'material':
                                                                          'Air'}, {'xyz': [28, 33, 1], 'material':
                                                                                            'Air'}, {'xyz': [28, 33, 2], 'material': 'Air'}, {
                                                                                                    'xyz': [28, 34,
                                                                                                                    1], 'material': 'Air'
                                                                                            }, {'xyz': [28, 34, 2], 'material':
                                                                                                    'Air'}, {'xyz': [28, 35, 1], 'material': 'Air'},
                  {'xyz': [28, 35, 2], 'material':
                    'Air'}, {'xyz': [28, 36, 1], 'material':
                                      'Air'}, {'xyz': [28, 36, 2], 'material':
                                                        'Air'}, {'xyz': [36, 27, 1], 'material':
                                                                          'Air'}, {'xyz': [36, 27, 2], 'material':
                                                                                            'Air'}, {'xyz': [36, 28, 1], 'material': 'Air'}, {
                                                                                                    'xyz': [36, 28,
                                                                                                                    2], 'material': 'Air'
                                                                                            }, {'xyz': [36, 29, 1], 'material':
                                                                                                    'Air'}, {'xyz': [36, 29, 2], 'material': 'Air'},
                  {'xyz': [36, 30, 1], 'material':
                    'Air'}, {'xyz': [36, 30, 2], 'material':
                                      'Air'}, {'xyz': [36, 31, 1], 'material':
                                                        'Air'}, {'xyz': [36, 31, 2], 'material':
                                                                          'Air'}, {'xyz': [36, 32, 1], 'material':
                                                                                            'Air'}, {'xyz': [36, 32, 2], 'material': 'Air'}, {
                                                                                                    'xyz': [36, 33,
                                                                                                                    1], 'material': 'Air'
                                                                                            }, {'xyz': [36, 33, 2], 'material':
                                                                                                    'Air'}, {'xyz': [36, 34, 1], 'material': 'Air'}, {
                                                                                                            'xyz': [36, 34,
                                                                                                                            2], 'material': 'Air'
                                                                                                    }, {'xyz': [36, 35, 1], 'material': 'Air'
                                                                                                            }, {'xyz': [36, 35, 2], 'material': 'Air'}, {
                                                                                                                    'xyz': [36, 36, 1], 'material': 'Air'
                                                                                                            }, {'xyz': [36, 36, 2], 'material': 'Air'}, {
                                                                                                                    'xyz': [37, 27, 1], 'material': 'Air'
                                                                                                            }, {'xyz': [37, 27, 2], 'material': 'Air'}, {
                                                                                                                    'xyz': [37, 28, 1], 'material': 'Air'
                                                                                                            }, {'xyz': [37, 28, 2], 'material': 'Air'}, {
                                                                                                                    'xyz': [37, 29, 1], 'material': 'Air'
                                                                                                            }, {'xyz': [37, 29, 2], 'material': 'Air'}, {
                                                                                                                    'xyz': [37, 30, 1], 'material': 'Air'
                                                                                                            }, {'xyz': [37, 30, 2], 'material': 'Air'}, {
                                                                                                                    'xyz': [37, 31, 1], 'material': 'Air'
                                                                                                            }, {'xyz': [37, 31, 2], 'material': 'Air'}, {
                                                                                                                    'xyz': [37, 32, 1], 'material': 'Air'
                                                                                                            }, {'xyz': [37, 32, 2], 'material': 'Air'}, {
                                                                                                                    'xyz': [37, 33, 1], 'material': 'Air'
                                                                                                            }, {'xyz': [37, 33, 2], 'material': 'Air'}, {
                                                                                                                    'xyz': [37, 34, 1], 'material': 'Air'
                                                                                                            }, {'xyz': [37, 34, 2], 'material': 'Air'}, {
                                                                                                                    'xyz': [37, 35, 1], 'material': 'Air'
                                                                                                            }, {'xyz': [37, 35, 2], 'material': 'Air'}, {
                                                                                                                    'xyz': [37, 36, 1], 'material': 'Air'
                                                                                                            }, {'xyz': [37, 36, 2], 'material': 'Air'}, {
                                                                                                                    'xyz': [38, 27, 1], 'material': 'Air'
                                                                                                            }, {'xyz': [38, 27, 2], 'material': 'Air'}, {
                                                                                                                    'xyz': [38, 28, 1], 'material': 'Air'
                                                                                                            }, {'xyz': [38, 28, 2], 'material': 'Air'}, {
                                                                                                                    'xyz': [38, 29, 1], 'material': 'Air'
                                                                                                            }, {'xyz': [38, 29, 2], 'material': 'Air'}, {
                                                                                                                    'xyz': [38, 30, 1], 'material': 'Air'
                                                                                                            }, {'xyz': [38, 30, 2], 'material': 'Air'}, {
                                                                                                                    'xyz': [38, 31, 1], 'material': 'Air'
                                                                                                            }, {'xyz': [38, 31, 2], 'material': 'Air'}, {
                                                                                                                    'xyz': [38, 32, 1], 'material': 'Air'
                                                                                                            }, {'xyz': [38, 32, 2], 'material': 'Air'}, {
                                                                                                                    'xyz': [38, 33, 1], 'material': 'Air'
                                                                                                            }, {'xyz': [38, 33, 2], 'material': 'Air'}, {
                                                                                                                    'xyz': [38, 34, 1], 'material': 'Air'
                                                                                                            }, {'xyz': [38, 34, 2], 'material': 'Air'}, {
                                                                                                                    'xyz': [38, 35, 1], 'material': 'Air'
                                                                                                            }, {'xyz': [38, 35, 2], 'material': 'Air'}, {
                                                                                                                    'xyz': [38, 36, 1], 'material': 'Air'
                                                                                                            }, {'xyz': [38, 36, 2], 'material': 'Air'}, {
                                                                                                                    'xyz': [39, 27, 1], 'material': 'Air'
                                                                                                            }, {'xyz': [39, 27, 2], 'material': 'Air'}, {
                                                                                                                    'xyz': [39, 28, 1], 'material': 'Air'
                                                                                                            }, {'xyz': [39, 28, 2], 'material': 'Air'}, {
                                                                                                                    'xyz': [39, 29, 1], 'material': 'Air'
                                                                                                            }, {'xyz': [39, 29, 2], 'material': 'Air'}, {
                                                                                                                    'xyz': [39, 30, 1], 'material': 'Air'
                                                                                                            }, {'xyz': [39, 30, 2], 'material': 'Air'}, {
                                                                                                                    'xyz': [39, 31, 1], 'material': 'Air'
                                                                                                            }, {'xyz': [39, 31, 2], 'material': 'Air'}, {
                                                                                                                    'xyz': [39, 32, 1], 'material': 'Air'
                                                                                                            }, {'xyz': [39, 32, 2], 'material': 'Air'}, {
                                                                                                                    'xyz': [39, 33, 1], 'material': 'Air'
                                                                                                            }, {'xyz': [39, 33, 2], 'material': 'Air'}, {
                                                                                                                    'xyz': [39, 34, 1], 'material': 'Air'
                                                                                                            }, {'xyz': [39, 34, 2], 'material': 'Air'}, {
                                                                                                                    'xyz': [39, 35, 1], 'material': 'Air'
                                                                                                            }, {'xyz': [39, 35, 2], 'material': 'Air'}, {
                                                                                                                    'xyz': [39, 36, 1], 'material': 'Air'
                                                                                                            }, {'xyz': [39, 36, 2], 'material': 'Air'}, {
                                                                                                                    'xyz': [40, 27, 1], 'material': 'Air'
                                                                                                            }, {'xyz': [40, 27, 2], 'material': 'Air'}, {
                                                                                                                    'xyz': [40, 28, 1], 'material': 'Air'
                                                                                                            }, {'xyz': [40, 28, 2], 'material': 'Air'}, {
                                                                                                                    'xyz': [40, 29, 1], 'material': 'Air'
                                                                                                            }, {'xyz': [40, 29, 2], 'material': 'Air'}, {
                                                                                                                    'xyz': [40, 30, 1], 'material': 'Air'
                                                                                                            }, {'xyz': [40, 30, 2], 'material': 'Air'}, {
                                                                                                                    'xyz': [40, 31, 1], 'material': 'Air'
                                                                                                            }, {'xyz': [40, 31, 2], 'material': 'Air'}, {
                                                                                                                    'xyz': [40, 32, 1], 'material': 'Air'
                                                                                                            }, {'xyz': [40, 32, 2], 'material': 'Air'}, {
                                                                                                                    'xyz': [40, 33, 1], 'material': 'Air'
                                                                                                            }, {'xyz': [40, 33, 2], 'material': 'Air'}, {
                                                                                                                    'xyz': [40, 34, 1], 'material': 'Air'
                                                                                                            }, {'xyz': [40, 34, 2], 'material': 'Air'}, {
                                                                                                                    'xyz': [40, 35, 1], 'material': 'Air'
                                                                                                            }, {'xyz': [40, 35, 2], 'material': 'Air'}, {
                                                                                                                    'xyz': [40, 36, 1], 'material': 'Air'
                                                                                                            }, {'xyz': [40, 36, 2], 'material': 'Air'}, {
                                                                                                                    'xyz': [41, 27, 1], 'material': 'Air'
                                                                                                            }, {'xyz': [41, 27, 2], 'material': 'Air'}, {
                                                                                                                    'xyz': [41, 28, 1], 'material': 'Air'
                                                                                                            }, {'xyz': [41, 28, 2], 'material': 'Air'}, {
                                                                                                                    'xyz': [41, 29, 1], 'material': 'Air'
                                                                                                            }, {'xyz': [41, 29, 2], 'material': 'Air'}, {
                                                                                                                    'xyz': [41, 30, 1], 'material': 'Air'
                                                                                                            }, {'xyz': [41, 30, 2], 'material': 'Air'}, {
                                                                                                                    'xyz': [41, 31, 1], 'material': 'Air'
                                                                                                            }, {'xyz': [41, 31, 2], 'material': 'Air'}, {
                                                                                                                    'xyz': [41, 32, 1], 'material': 'Air'
                                                                                                            }, {'xyz': [41, 32, 2], 'material': 'Air'}, {
                                                                                                                    'xyz': [41, 33, 1], 'material': 'Air'
                                                                                                            }, {'xyz': [41, 33, 2], 'material': 'Air'}, {
                                                                                                                    'xyz': [41, 34, 1], 'material': 'Air'
                                                                                                            }, {'xyz': [41, 34, 2], 'material': 'Air'}, {
                                                                                                                    'xyz': [41, 35, 1], 'material': 'Air'
                                                                                                            }, {'xyz': [41, 35, 2], 'material': 'Air'}, {
                                                                                                                    'xyz': [41, 36, 1], 'material': 'Air'
                                                                                                            }, {'xyz': [41, 36, 2], 'material': 'Air'}, {
                                                                                                                    'xyz': [42, 27, 1], 'material': 'Air'
                                                                                                            }, {'xyz': [42, 27, 2], 'material': 'Air'}, {
                                                                                                                    'xyz': [42, 28, 1], 'material': 'Air'
                                                                                                            }, {'xyz': [42, 28, 2], 'material': 'Air'}, {
                                                                                                                    'xyz': [42, 29, 1], 'material': 'Air'
                                                                                                            }, {'xyz': [42, 29, 2], 'material': 'Air'}, {
                                                                                                                    'xyz': [42, 30, 1], 'material': 'Air'
                                                                                                            }, {'xyz': [42, 30, 2], 'material': 'Air'}, {
                                                                                                                    'xyz': [42, 31, 1], 'material': 'Air'
                                                                                                            }, {'xyz': [42, 31, 2], 'material': 'Air'}, {
                                                                                                                    'xyz': [42, 32, 1], 'material': 'Air'
                                                                                                            }, {'xyz': [42, 32, 2], 'material': 'Air'}, {
                                                                                                                    'xyz': [42, 33, 1], 'material': 'Air'
                                                                                                            }, {'xyz': [42, 33, 2], 'material': 'Air'}, {
                                                                                                                    'xyz': [42, 34, 1], 'material': 'Air'
                                                                                                            }, {'xyz': [42, 34, 2], 'material': 'Air'}, {
                                                                                                                    'xyz': [42, 35, 1], 'material': 'Air'
                                                                                                            }, {'xyz': [42, 35, 2], 'material': 'Air'}, {
                                                                                                                    'xyz': [42, 36, 1], 'material': 'Air'
                                                                                                            }, {'xyz': [42, 36, 2], 'material': 'Air'}, {
                                                                                                                    'xyz': [43, 27, 1], 'material': 'Air'
                                                                                                            }, {'xyz': [43, 27, 2], 'material': 'Air'}, {
                                                                                                                    'xyz': [43, 28, 1], 'material': 'Air'
                                                                                                            }, {'xyz': [43, 28, 2], 'material': 'Air'}, {
                                                                                                                    'xyz': [43, 29, 1], 'material': 'Air'
                                                                                                            }, {'xyz': [43, 29, 2], 'material': 'Air'}, {
                                                                                                                    'xyz': [43, 30, 1], 'material': 'Air'
                                                                                                            }, {'xyz': [43, 30, 2], 'material': 'Air'}, {
                                                                                                                    'xyz': [43, 31, 1], 'material': 'Air'
                                                                                                            }, {'xyz': [43, 31, 2], 'material': 'Air'}, {
                                                                                                                    'xyz': [43, 32, 1], 'material': 'Air'
                                                                                                            }, {'xyz': [43, 32, 2], 'material': 'Air'}, {
                                                                                                                    'xyz': [43, 33, 1], 'material': 'Air'
                                                                                                            }, {'xyz': [43, 33, 2], 'material': 'Air'}, {
                                                                                                                    'xyz': [43, 34, 1], 'material': 'Air'
                                                                                                            }, {'xyz': [43, 34, 2], 'material': 'Air'}, {
                                                                                                                    'xyz': [43, 35, 1], 'material': 'Air'
                                                                                                            }, {'xyz': [43, 35, 2], 'material': 'Air'}, {
                                                                                                                    'xyz': [43, 36, 1], 'material': 'Air'
                                                                                                            }, {'xyz': [43, 36, 2], 'material': 'Air'}, {
                                                                                                                    'xyz': [44, 27, 1], 'material': 'Air'
                                                                                                            }, {'xyz': [44, 27, 2], 'material': 'Air'}, {
                                                                                                                    'xyz': [44, 28, 1], 'material': 'Air'
                                                                                                            }, {'xyz': [44, 28, 2], 'material': 'Air'}, {
                                                                                                                    'xyz': [44, 29, 1], 'material': 'Air'
                                                                                                            }, {'xyz': [44, 29, 2], 'material': 'Air'}, {
                                                                                                                    'xyz': [44, 30, 1], 'material': 'Air'
                                                                                                            }, {'xyz': [44, 30, 2], 'material': 'Air'}, {
                                                                                                                    'xyz': [44, 31, 1], 'material': 'Air'
                                                                                                            }, {'xyz': [44, 31, 2], 'material': 'Air'}, {
                                                                                                                    'xyz': [44, 32, 1], 'material': 'Air'
                                                                                                            }, {'xyz': [44, 32, 2], 'material': 'Air'}, {
                                                                                                                    'xyz': [44, 33, 1], 'material': 'Air'
                                                                                                            }, {'xyz': [44, 33, 2], 'material': 'Air'}, {
                                                                                                                    'xyz': [44, 34, 1], 'material': 'Air'
                                                                                                            }, {'xyz': [44, 34, 2], 'material': 'Air'}, {
                                                                                                                    'xyz': [44, 35, 1], 'material': 'Air'
                                                                                                            }, {'xyz': [44, 35, 2], 'material': 'Air'}, {
                                                                                                                    'xyz': [44, 36, 1], 'material': 'Air'
                                                                                                            }, {'xyz': [44, 36, 2], 'material': 'Air'}, {
                                                                                                                    'xyz': [45, 27, 1], 'material': 'Air'
                                                                                                            }, {'xyz': [45, 27, 2], 'material': 'Air'}, {
                                                                                                                    'xyz': [45, 28, 1], 'material': 'Air'
                                                                                                            }, {'xyz': [45, 28, 2], 'material': 'Air'}, {
                                                                                                                    'xyz': [45, 29, 1], 'material': 'Air'
                                                                                                            }, {'xyz': [45, 29, 2], 'material': 'Air'}, {
                                                                                                                    'xyz': [45, 30, 1], 'material': 'Air'
                                                                                                            }, {'xyz': [45, 30, 2], 'material': 'Air'}, {
                                                                                                                    'xyz': [45, 31, 1], 'material': 'Air'
                                                                                                            }, {'xyz': [45, 31, 2], 'material': 'Air'}, {
                                                                                                                    'xyz': [45, 32, 1], 'material': 'Air'
                                                                                                            }, {'xyz': [45, 32, 2], 'material': 'Air'}, {
                                                                                                                    'xyz': [45, 33, 1], 'material': 'Air'
                                                                                                            }, {'xyz': [45, 33, 2], 'material': 'Air'}, {
                                                                                                                    'xyz': [45, 34, 1], 'material': 'Air'
                                                                                                            }, {'xyz': [45, 34, 2], 'material': 'Air'}, {
                                                                                                                    'xyz': [45, 35, 1], 'material': 'Air'
                                                                                                            }, {'xyz': [45, 35, 2], 'material': 'Air'}, {
                                                                                                                    'xyz': [45, 36, 1], 'material': 'Air'
                                                                                                            }, {'xyz': [45, 36, 2], 'material': 'Air'}, {
                                                                                                                    'xyz': [46, 27, 1], 'material': 'Air'
                                                                                                            }, {'xyz': [46, 27, 2], 'material': 'Air'}, {
                                                                                                                    'xyz': [46, 28, 1], 'material': 'Air'
                                                                                                            }, {'xyz': [46, 28, 2], 'material': 'Air'}, {
                                                                                                                    'xyz': [46, 29, 1], 'material': 'Air'
                                                                                                            }, {'xyz': [46, 29, 2], 'material': 'Air'},
                  {'xyz': [46, 30, 1], 'material':
                    'Air'}, {'xyz': [46, 30, 2], 'material':
                                      'Air'}, {'xyz': [46, 31, 1], 'material':
                                                        'Air'}, {'xyz': [46, 31, 2], 'material':
                                                                          'Air'}, {'xyz': [46, 32, 1], 'material':
                                                                                            'Air'}, {'xyz': [46, 32, 2], 'material': 'Air'
                                                                                                              }, {'xyz': [46, 33, 1], 'material': 'Air'},
                  {'xyz': [46, 33, 2], 'material':
                    'Air'}, {'xyz': [46, 34, 1], 'material':
                                      'Air'}, {'xyz': [46, 34, 2], 'material':
                                                        'Air'}, {'xyz': [46, 35, 1], 'material':
                                                                          'Air'}, {'xyz': [46, 35, 2], 'material':
                                                                                            'Air'}, {'xyz': [46, 36, 1], 'material': 'Air'
                                                                                                              }, {'xyz': [46, 36, 2], 'material': 'Air'}]
        }, ""


    return None
