"""
Hire calculations
"""
from datetime import date
from functools import lru_cache
from typing import Optional

from clearcut import get_logger

from pycasting.calc.predictors import PredictedCompanyState, predict, PredictorCategory
from pycasting.dataclasses.predictions import Role
from pycasting.misc import MonthYear

logger = get_logger(__name__)


@lru_cache
def hires_through_effective_date(effective_date: date, role: Role, state: Optional[PredictedCompanyState] = None) -> int:
    """Calculate how many people would have been hired through the effective date."""
    # hire_predictor is a model that has a "name" and other params. The name matches to a registered predictor function
    # in the `predictors.py` file, and the params should get passed into that function (along with the state).
    # It will return an amount which is the (float) value we're looking for.
    dataclass = role.hire_predictor
    params = dataclass.dict(exclude={"name"})

    return round(predict(PredictorCategory.headcount, dataclass.name, effective_date, params, state=state))


@lru_cache
def hires_in_month(month_year: MonthYear, role: Role, state: Optional[PredictedCompanyState] = None) -> int:
    """Calculate how many people would have been hired in this month."""
    end_hires = hires_through_effective_date(month_year.end_of_month, role, state)
    start_hires = hires_through_effective_date(month_year.shift_month(-1).end_of_month, role, state)

    logger.debug(f"start: {start_hires}")
    logger.debug(f"end: {end_hires}")
    return end_hires - start_hires
