from datetime import timedelta, date
from enum import Enum

import pydantic.json
from pydantic import BaseModel, Field
from uncertainties.core import Variable, ufloat_fromstr

from pycasting.dataclasses.scenario import Actuals


class State(BaseModel):
    """Contains current "state" at a future date. Passed into predictors to be used when modelling various aspects of the future"""

    effective_date: date = Field(..., description="How far in the future we are")

    number_of_customers: int = Field(..., description="Number of on-boarded customers at this point in time.")
    actuals: Actuals = Field(..., description="Latest known actual information (financial, etc.)")


class PredictorCategory(Enum):
    usage = "usage"
    headcount = "headcount"


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


pydantic.json.ENCODERS_BY_TYPE[Variable] = lambda v: str(v)
