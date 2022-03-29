"""
Usage-over-time predictor predictors. To add a new predictors, define a function here that takes in a timedelta, initialized with arbitrary
other kwargs, and returns a positive value which represents the usage amount at that point in time. Also decorate it accordingly.
"""
from datetime import timedelta

from pycasting.predicting.misc import UFloat, State


def linear(state: State, *, initial_usage: UFloat, increase_per_year: UFloat) -> UFloat:
    # Value is mx+b, where b = initial_usage, and m = %rate * initial_usage. Have to consider units though.
    return initial_usage + initial_usage * increase_per_year * (state.offset / timedelta(days=360))
