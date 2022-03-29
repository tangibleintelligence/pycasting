"""
Details of the team. Hires, costs, etc.
"""
from typing import Dict, Union

from pydantic import BaseModel, Field


# May want to take more detailed process from pylanner
class EmployeeCosts(BaseModel):
    annual_fixed: float = 10000 + 3000  # Incl health insurance and other subscriptions
    annual_percent: float = 0.076 + 0.04


class HireModel(BaseModel):
    """Calls to corresponding function in predicting/headcount.py"""

    name: str
    params: Dict[str, Union[float, str]]


class Role(BaseModel):
    """High-level "role". Average sal and count level detail only."""

    name: str
    salary: float
    hire_model: HireModel


class SalesRole(Role):
    """Extends `Role` to support commission compensation"""

    commission_percent: float = Field(..., ge=0, le=1)
