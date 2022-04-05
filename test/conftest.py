from datetime import date

import pytest
from uncertainties import ufloat

from pycasting.dataclasses.predictions import SalesRole, CustomerType, COGS
from pycasting.misc import BaseModel, UFloat


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


class LinearUsagePredictor(BaseModel):
    # Would be dynamically generated in code
    # Based on linear growth
    name: str = "linear"
    initial_usage: UFloat = ufloat(1000, 100)
    increase_per_year: UFloat = ufloat(1, 0.5)


@pytest.fixture
def linear_usage_predictor() -> LinearUsagePredictor:
    return LinearUsagePredictor()


@pytest.fixture
def simple_customer_type(linear_usage_predictor) -> CustomerType:
    return CustomerType(
        name="general",
        monthly_fee=ufloat(0, 0),
        setup_fee=ufloat(10000, 0),
        usage_fee=0.05,
        usage_predictor=linear_usage_predictor,
        fraction_of_total_customers=1,
        cogs=COGS(
            monthly=ufloat(0, 0),
            per_usage=ufloat(0, 0),
        ),
    )
