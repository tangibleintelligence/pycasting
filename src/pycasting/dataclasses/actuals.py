"""
Pydantic data objects used to represent reality.
"""

import warnings
from datetime import datetime, date
from typing import Dict

from clearcut import get_logger
from frozendict import frozendict
from pydantic import validator

from pycasting.misc import BaseModel, is_end_of_month, end_of_month, MonthYear

logger = get_logger(__name__)


class Actuals(BaseModel):
    accurate_as_of: date = datetime.now().date()
    active_customers: Dict[str, int] = frozendict()

    @property
    def first_unknown_month_year(self) -> MonthYear:
        return MonthYear.from_date(self.accurate_as_of).shift_month(1)

    @validator('active_customers')
    def freeze_dict(cls, v):
        if isinstance(v, dict):
            return frozendict(v)
        else:
            return v

    @validator("accurate_as_of")
    def accurate_as_of_val(cls, v):
        if v > datetime.now().date():
            warnings.warn("`accurate_as_of` date set in the future. This is not intended.")

        # Enforce EOM
        if not is_end_of_month(v):
            logger.warning(f"Coercing effective date to EOM: {v} -> {end_of_month(v)}")
            return end_of_month(v)
        else:
            return v
