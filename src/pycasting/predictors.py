"""Functions which are used to define expected changes over time."""
import math
from collections import defaultdict
from datetime import timedelta, date
from enum import Enum
from typing import Dict, Callable, Optional, List

from pydantic import BaseModel, Field

from pycasting.dataclasses.actuals import Actuals
from pycasting.misc import UFloat


class PredictedCompanyState(BaseModel):
    """
    Contains predicted "state" of the company at a future date. Passed into predictors to be used when modelling various aspects of the
    future
    """

    effective_date: date = Field(..., description="How far in the future we are")
    number_of_customers: int = Field(..., description="Number of on-boarded customers at this point in time.")
    actuals: Actuals = Field(..., description="Latest known actual information (financial, etc.)")


class PredictorCategory(Enum):
    usage = "usage"
    headcount = "headcount"


_predictor_registry: Dict[PredictorCategory, Dict[str, Callable]] = defaultdict(defaultdict)


def register_predictor(category: PredictorCategory, name: Optional[str] = None):
    """Decorate a predictor function to associate it with a category/name and make it available for use."""

    def with_register(fn, name_=name):
        _predictor_registry[category][name_ or fn.__name__] = fn

        return fn

    return with_register


def get_predictor(category: PredictorCategory, name: str):
    predictor_fn = _predictor_registry.get(category, {}).get(name, None)
    if predictor_fn is None:
        raise ValueError(f"No matching predictor: {category} | {name}")
    else:
        return predictor_fn


def get_predictor_names(category: PredictorCategory) -> List[str]:
    return list(_predictor_registry.get(category, {}).keys())


"""
Headcount-over-time predictors.
"""


@register_predictor(PredictorCategory.headcount, "constant")
def constant_hc(state: PredictedCompanyState, *, count: int) -> int:
    return count


@register_predictor(PredictorCategory.headcount)
def linear_with_max(
    state: PredictedCompanyState, *, initial_count: int, hires_per_year: int, first_hire_date: date, max_hires: int
) -> int:
    if state.effective_date < first_hire_date:
        return 0

    # Determine how long between first_hire_date and effective_date.
    time_since_first_hire: timedelta = state.effective_date - first_hire_date

    # Linear since first hire at the rate given
    current_hires = math.floor(initial_count + initial_count * hires_per_year * (time_since_first_hire / timedelta(days=360)))

    return min(current_hires, max_hires)


@register_predictor(PredictorCategory.headcount)
def scale_with_customers(state: PredictedCompanyState, *, customers_per_person: int) -> int:
    """Scales with number of customers onboarded."""
    return math.ceil(state.number_of_customers / customers_per_person)


"""
Usage-over-time predictor predictors. These are provided an additional argument called "start" which is when the customer was "turned on".
"""


@register_predictor(PredictorCategory.usage, "linear")
def linear_usage(state: PredictedCompanyState, start: date, *, initial_usage: UFloat, increase_per_year: UFloat) -> UFloat:
    if state.effective_date < start:
        return UFloat(0, 0)

    offset: timedelta = state.effective_date - start
    # Expecting linear growth since "turned on" `offset` ago.
    return initial_usage + initial_usage * increase_per_year * (offset / timedelta(days=360))


@register_predictor(PredictorCategory.usage, "constant")
def constant_usage(state: PredictedCompanyState, start: date, *, initial_usage: UFloat) -> UFloat:
    if state.effective_date < start:
        return UFloat(0, 0)
    else:
        return initial_usage
