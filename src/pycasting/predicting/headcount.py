"""
Headcount-over-time predictors. To add a new predictor, define a function here that takes in a timedelta, initialized with arbitrary other
kwargs, and returns a positive value which represents the headcount at that point in time. Also decorate it accordingly.
"""
import math
from datetime import timedelta, date

from pycasting.predicting.misc import State


# @predictor(PredictorCategory.headcount, "constant")
def constant(state: State, *, count: int) -> int:
    return count


# @predictor(PredictorCategory.headcount, "linear")
def linear_with_max(state: State, *, initial_count: int, hires_per_quarter: int, first_hire_date: date, max_hires: int) -> int:
    # Determine how long between first_hire_date and offset (from now)
    # Value is mx+b, where b = initial_usage, and m = %rate * initial_usage. Have to consider units though.
    return math.floor(initial_count + initial_count * hires_per_quarter * (state.offset / timedelta(days=90)))


def scale_with_customers(state, *, customers_per_person: int) -> int:
    """Scales with number of customers onboarded."""
    return math.ceil(state.number_of_customers / customers_per_person)
