"""
Pydantic data objects used to represent reality.
"""

import warnings
from datetime import datetime, date

from pydantic import validator

from pycasting.misc import BaseModel


class Actuals(BaseModel):
    accurate_as_of: date = datetime.now().date()

    @validator("accurate_as_of")
    def not_future(cls, v):
        if v > datetime.now().date():
            warnings.warn("`accurate_as_of` date set in the future. This is not intended.")

        return v
