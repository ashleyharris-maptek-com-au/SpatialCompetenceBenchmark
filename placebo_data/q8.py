import math
from textwrap import dedent


def get_response(subPass: int):
    """Get the placebo response for this question."""
    if subPass == 0:
        return {
                'function':
                dedent("""
                        def f(x,y):
                                return -162*x*x*x - 854*x*x + 945*x + 653*y*y*y - 1881*y*y - 145*y + 2829
                """.strip())
        }, "Placebo thinking... hmmm..."

    if subPass == 1:
        return {
                'function':
                dedent("""
                        def f(x,y):
                                return -5 * x - 4 * y + 30
                """.strip())
        }, "Placebo thinking... hmmm..."

    if subPass == 3:
        return {
                'function':
                dedent("""
                        def f(x,y):
                                return ((x-0)**2+(y-0)**2) * ((x-0)**2+(y-1)**2) * ((x-0)**2+(y-2)**2) * ((x-0)**2+(y-3)**2) * ((x-0)**2+(y-4)**2) * ((x-0)**2+(y-5)**2) * ((x-1)**2+(y-0)**2) * ((x-1)**2+(y-1)**2) * ((x-1)**2+(y-2)**2) * ((x-1)**2+(y-3)**2) * ((x-1)**2+(y-7)**2) * ((x-2)**2+(y-0)**2) * ((x-2)**2+(y-1)**2) * ((x-2)**2+(y-2)**2) * ((x-2)**2+(y-6)**2) * ((x-2)**2+(y-7)**2) * ((x-3)**2+(y-0)**2) * ((x-3)**2+(y-1)**2) * ((x-3)**2+(y-5)**2) * ((x-3)**2+(y-6)**2) * ((x-3)**2+(y-7)**2) * ((x-4)**2+(y-0)**2) * ((x-4)**2+(y-1)**2) * ((x-4)**2+(y-5)**2) * ((x-4)**2+(y-6)**2) * ((x-4)**2+(y-7)**2) * ((x-5)**2+(y-0)**2) * ((x-5)**2+(y-1)**2) * ((x-5)**2+(y-2)**2) * ((x-5)**2+(y-6)**2) * ((x-5)**2+(y-7)**2) * ((x-6)**2+(y-0)**2) * ((x-6)**2+(y-1)**2) * ((x-6)**2+(y-2)**2) * ((x-6)**2+(y-3)**2) * ((x-6)**2+(y-7)**2) * ((x-7)**2+(y-0)**2) * ((x-7)**2+(y-1)**2) * ((x-7)**2+(y-2)**2) * ((x-7)**2+(y-3)**2) * ((x-7)**2+(y-4)**2) * ((x-7)**2+(y-5)**2) - 1
                """.strip())
        }, "Placebo thinking... hmmm..."


    return None
