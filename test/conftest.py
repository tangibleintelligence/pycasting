from datetime import date, timedelta

import pytest
from uncertainties import ufloat

from pycasting.pydanticmodels.actuals import Actuals
from pycasting.pydanticmodels.predictions import SalesRole, CustomerType, COGS, LeadStage, LeadConfig, OtherSpend
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
def actuals(simple_customer_type) -> Actuals:
    return Actuals(accurate_as_of=date(2024, 12, 31), active_customers={simple_customer_type.name: 0})


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
def initial_lead_stage() -> LeadStage:
    return LeadStage(name="initial", duration=timedelta(days=10), conversion_rate=0.75)


@pytest.fixture
def close_lead_stage() -> LeadStage:
    return LeadStage(name="close", duration=timedelta(days=35), conversion_rate=0.5)


@pytest.fixture
def simple_lead_config(initial_lead_stage, close_lead_stage):
    return LeadConfig(
        stages=(
            initial_lead_stage,
            close_lead_stage,
        ),
        cost_per_ad_click=0.20,
        qualified_lead_to_click_ratio=0.01,
    )


@pytest.fixture
def rent():
    return OtherSpend(name="Rent", monthly=2700)


@pytest.fixture
def simple_customer_type(linear_usage_predictor, simple_lead_config) -> CustomerType:
    return CustomerType(
        name="general",
        monthly_fee=ufloat(0, 0),
        setup_fee=ufloat(1, 0),
        usage_fee=0.05,
        usage_predictor=linear_usage_predictor,
        fraction_of_leads=1,
        cogs=COGS(
            monthly=ufloat(50, 0),
            per_usage=ufloat(0.01, 0),
        ),
        lead_config=simple_lead_config,
        churn=0.5,
        payment_months_behind=1,
    )
