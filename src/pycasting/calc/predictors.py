"""Functions which are used to define expected changes over time."""
import math
from collections import defaultdict
from datetime import timedelta, date
from enum import Enum
from typing import Dict, Callable, Optional, List, Tuple, Any, Union

from clearcut import get_logger
from pydantic import Field, validator

from pycasting.dataclasses.actuals import Actuals
from pycasting.misc import UFloat, BaseModel, MonthYear, is_end_of_month, end_of_month

logger = get_logger(__name__)


class PredictedCompanyState(BaseModel):
    """
    Contains predicted "state" of the company at a future date. Passed into predictors to be used when modelling various aspects of the
    future
    """

    effective_date: date = Field(..., description="How far in the future we are")
    number_of_customers: int = Field(..., description="Number of on-boarded customers at this point in time.")
    actuals: Actuals = Field(..., description="Latest known actual information (financial, etc.)")

    @validator("effective_date")
    def enforce_end_of_month(cls, v):
        """Always use the end of the month as the effective date."""
        if not is_end_of_month(v):
            logger.warning(f"Coercing effective date to EOM: {v} -> {end_of_month(v)}")
            return end_of_month(v)
        else:
            return v

    @property
    def effective_month_year(self) -> MonthYear:
        return MonthYear(month=self.effective_date.month, year=self.effective_date.year)

    # These aren't perfect because they don't adjust the number of customers. TODO need to determine if rework is needed.
    def with_effective_date(self, effective_date: date) -> "PredictedCompanyState":
        return PredictedCompanyState(effective_date=effective_date, **self.dict(exclude={"effective_date"}))

    def with_effective_month_year(self, month_year: MonthYear) -> "PredictedCompanyState":
        return self.with_effective_date(month_year.end_of_month)

    def with_shifted_month_year(self, shift_amount: int) -> "PredictedCompanyState":
        """Convenience function that returns a new state with the effective date shifted by the given value."""
        return self.with_effective_month_year(self.effective_month_year.shift_month(shift_amount))


class PredictorCategory(Enum):
    usage = "usage"
    headcount = "headcount"


_predictor_registry: Dict[PredictorCategory, Dict[str, Tuple[Callable, bool]]] = defaultdict(defaultdict)


def register_predictor(category: PredictorCategory, name: Optional[str] = None, state_dependent: bool = False):
    """
    Decorate a predictor function to associate it with a category/name and make it available for use.

    If `state_dependent` is true, then this predictor will depend on the future state of the company. Care should
    be taken as this can cause infinite loops.
    """

    def with_register(fn, name_=name):
        _predictor_registry[category][name_ or fn.__name__] = fn, state_dependent

        return fn

    return with_register


def get_predictor(category: PredictorCategory, name: str):
    predictor_fn = _predictor_registry.get(category, {}).get(name, None)
    if predictor_fn is None:
        raise ValueError(f"No matching predictor: {category} | {name}")
    else:
        return predictor_fn[0]


def predict(
    category: PredictorCategory,
    name: str,
    effective_date: date,
    params: Dict[str, Any] = None,
    start: Optional[date] = None,
    state: Optional[PredictedCompanyState] = None,
) -> Union[int, UFloat]:
    predictor_fn, state_dependent = _predictor_registry.get(category, {}).get(name)

    if state_dependent and state is None:
        raise RuntimeError("State not passed for state dependent prediction")
    if category is PredictorCategory.usage and start is None:
        raise RuntimeError("start not passed for usage predictor")

    kwargs = dict()
    kwargs["effective_date"] = effective_date
    if state_dependent:
        kwargs["state"] = state
    if params is not None:
        kwargs.update(params)
    if start is not None:
        kwargs["start"] = start

    return predictor_fn(**kwargs)


def get_predictor_names(category: PredictorCategory) -> List[str]:
    return list(_predictor_registry.get(category, {}).keys())


"""
Headcount-over-time predictors.
"""


@register_predictor(PredictorCategory.headcount, "constant")
def constant_hc(*, effective_date: date, count: int) -> int:
    return count


@register_predictor(PredictorCategory.headcount)
def linear_with_max(*, effective_date: date, initial_count: int, hires_per_year: int, first_hire_date: date, max_hires: int) -> int:
    if effective_date < first_hire_date:
        return 0

    # Determine how long between first_hire_date and effective_date.
    time_since_first_hire: timedelta = effective_date - first_hire_date

    # Linear since first hire at the rate given
    current_hires = math.floor(initial_count + initial_count * hires_per_year * (time_since_first_hire / timedelta(days=360)))

    return min(current_hires, max_hires)


@register_predictor(PredictorCategory.headcount, state_dependent=True)
def scale_with_customers(*, effective_date: date, state: PredictedCompanyState, customers_per_person: int) -> int:
    """Scales with number of customers onboarded."""
    return math.ceil(state.number_of_customers / customers_per_person)


"""
Usage-over-time predictor predictors. These are provided an additional argument called "start" which is when the customer was "turned on".
"""


@register_predictor(PredictorCategory.usage, "linear")
def linear_usage(*, effective_date: date, start: date, initial_usage: UFloat, increase_per_year: UFloat) -> UFloat:
    if effective_date < start:
        return UFloat(0, 0)

    offset: timedelta = effective_date - start
    # Expecting linear growth since "turned on" `offset` ago.
    return initial_usage + initial_usage * increase_per_year * (offset / timedelta(days=360))


@register_predictor(PredictorCategory.usage, "constant")
def constant_usage(*, effective_date: date, start: date, initial_usage: UFloat) -> UFloat:
    if effective_date < start:
        return UFloat(0, 0)
    else:
        return initial_usage
