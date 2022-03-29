"""
Top-level scenario wrapper
"""
from typing import List

from pydantic import BaseModel

from pycasting.dataclasses.budget import LeadConfig, CustomerType


class Scenario(BaseModel):
    lead_config: LeadConfig
    customer_types: List[CustomerType]
