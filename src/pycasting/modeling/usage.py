"""
Usage-over-time models. To add a new model, define a function here that takes in a timedelta, initialized with arbitrary other kwargs, and
returns a positive value which represents the usage amount at that point in time.
"""
from datetime import timedelta

from pycasting.modeling.misc import UFloat


def linear(initial_usage: UFloat, offset: timedelta, *, rate_per_30_days: UFloat) -> UFloat:
    # Value is mx+b, where b = initial_usage, and m = %rate * initial_usage. Have to consider units though.
    # as an example, if initial_usage = 100 and % rate per month = 50%, then:
    #   - at t=0, u = initial_usage
    #   - at t=1 month, u = 1.5 * initial_usage
    #   - at t = 2 month, u = 2 * initial_usage
    return initial_usage + initial_usage * rate_per_30_days * (offset / timedelta(days=30))
