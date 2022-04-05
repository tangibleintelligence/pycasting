from datetime import date

import pytest

from pycasting.dataclasses.predictions import SalesRole
from pycasting.misc import BaseModel


class SalespersonHirePredictor(BaseModel):
    # Would be dynamically generated in code
    # Based on linear growth
    name: str = "linear_with_max"
    initial_count: int = 1
    hires_per_year: int = 12
    first_hire_date: date = date(2025, 1, 1)
    max_hires: int = 10


@pytest.fixture
def salesperson_hire_predictor() -> SalespersonHirePredictor:
    return SalespersonHirePredictor()


@pytest.fixture
def salesperson_role(salesperson_hire_predictor) -> SalesRole:
    return SalesRole(
        name="Salesperson",
        salary=50000,
        hire_predictor=salesperson_hire_predictor,
        commission_percent=0.15,
        ramp_up_months=3,
        monthly_quota=40,
    )
