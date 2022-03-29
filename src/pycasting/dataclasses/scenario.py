"""
Top-level scenario wrapper
"""
import warnings
from datetime import date, datetime
from typing import List, Union

from pydantic import BaseModel, validator

from pycasting.dataclasses.customer import LeadConfig, CustomerType
from pycasting.dataclasses.headcount import EmployeeCosts, SalesRole, Role


class Actuals(BaseModel):
    accurate_as_of: date

    @validator("accurate_as_of")
    def not_future(cls, v):
        if v > datetime.now():
            warnings.warn("accurate as of date set in the future. This is not intended.")

        return v


class Scenario(BaseModel):
    lead_config: LeadConfig
    customer_types: List[CustomerType]
    headcount: List[Union[SalesRole, Role]]
    employee_costs: EmployeeCosts = EmployeeCosts()

    @validator("customer_types")
    def customer_types_add_to_1(cls, v):
        fracs = [getattr(x, "fraction_of_total_customers") for x in v]
        if sum(fracs) != 1.0:
            raise ValueError(f"Total customer fractions must add to 1, not {sum(fracs)}")

        return v
