"""
SaaS Budgeting objects.
"""
from datetime import timedelta
from typing import List, Union, Dict

from pydantic import BaseModel, Field

from pycasting.modeling.misc import UFloat


class LeadStage(BaseModel):
    """Step of the opportunity to customer process."""

    name: str
    duration: timedelta
    conversion_rate: float = Field(..., ge=0, le=1)


class LeadConfig(BaseModel):
    lead_quota_per_sales_rep: int
    stages: List[LeadStage]


class UsageModel(BaseModel):
    """Models the usage amount of a customer over time."""

    name: str
    params: Dict[str, Union[float, str]]


class CustomerType(BaseModel):
    name: str
    monthly_fee: UFloat
    setup_fee: UFloat
    usage_fee: UFloat
    usage_model: UsageModel
