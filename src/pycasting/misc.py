from datetime import date
from functools import total_ordering
from typing import Any, Iterator

import pydantic.json
from dateutil.relativedelta import relativedelta
from pydantic import Field, BaseModel as PydanticBaseModel, BaseConfig as PydanticBaseConfig
from uncertainties import ufloat_fromstr
from uncertainties.core import Variable


# noinspection PyUnresolvedReferences
class UFloat(Variable):
    """A float with uncertainty."""

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if isinstance(v, str):
            return ufloat_fromstr(v)
        elif isinstance(v, Variable):
            return v
        else:
            raise ValueError("must be a str or a ufloat")

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema["type"] = "string"
        field_schema["description"] = (
            "If no uncertainty is specified, assumes +- 1 on the last digit. "
            "See <https://pythonhosted.org/uncertainties/user_guide.html#creating-numbers-with-uncertainties> for more."
        )
        field_schema["pattern"] = r"^((?:(\d\.*)+(?:\+\/\-|±)(\d\.*)+)|(?:(\d\.*)+(?:\((\d\.*)+\))?))$"
        # Technically the library can parse lots more regex forms, but this keeps it simple

    # No-ops to make code completion more happy
    def __add__(self, other):
        return super().__add__(other)

    def __radd__(self, other):
        return super().__radd__(other)

    def __mul__(self, other):
        return super().__mul__(other)

    def __rmul__(self, other):
        return super().__rmul__(other)

    def __pow__(self, power, modulo=None):
        return super().__pow__(power, modulo)

    def __rpow__(self, other):
        return super().__rpow__(other)

    def __truediv__(self, other):
        return super().__truediv__(other)

    def __rtruediv__(self, other):
        return super().__rtruediv__(other)

    def __lt__(self, other):
        return super().__lt__(other)

    def __gt__(self, other):
        return super().__gt__(other)

    def __le__(self, other):
        return super().__le__(other)

    def __ge__(self, other):
        return super().__ge__(other)


class BaseModel(PydanticBaseModel):
    class Config(PydanticBaseConfig):
        frozen = True


def end_of_month(d: date) -> date:
    return d + relativedelta(day=1, months=1, days=-1)


def is_end_of_month(d: date) -> bool:
    return (d + relativedelta(days=1)).day == 1


@total_ordering
class MonthYear(BaseModel):
    """Handles month-level data, and addition/subtraction"""

    month: int = Field(..., ge=1, le=12)
    year: int

    def __eq__(self, other: Any) -> bool:
        assert isinstance(other, MonthYear)
        return self.year == other.year and self.month == other.month

    def __lt__(self, other):
        assert isinstance(other, MonthYear)
        return self.start_of_month < other.start_of_month

    @property
    def start_of_month(self) -> date:
        return date(self.year, self.month, 1)

    @property
    def end_of_month(self) -> date:
        return end_of_month(self.start_of_month)

    def shift_month(self, shift_amount: int) -> "MonthYear":
        """Shifts months by shift_amount, wrapping around years, returning a new `MonthYear` object."""
        new_start_of_month = self.start_of_month + relativedelta(months=shift_amount)
        return MonthYear(month=new_start_of_month.month, year=new_start_of_month.year)

    @classmethod
    def from_date(cls, dt: date):
        return cls(month=dt.month, year=dt.year)

    @classmethod
    def between(cls, start: "MonthYear", end: "MonthYear", inclusive: bool = True) -> Iterator["MonthYear"]:
        if inclusive is False:
            end = end.shift_month(-1)

        month_year = start
        while month_year <= end:
            yield month_year
            month_year = month_year.shift_month(1)


pydantic.json.ENCODERS_BY_TYPE[Variable] = lambda v: str(v)
