"""
Pydantic data objects used for prediction
"""
import inspect
from datetime import timedelta
from typing import List, Dict, Union, Tuple

from pydantic import Field, validator, create_model

from pycasting.misc import UFloat, BaseModel
from pycasting.calc.predictors import get_predictor_names, PredictorCategory, get_predictor

"""
Details of customers (potential, etc.)
"""


class LeadStage(BaseModel):
    """Step of the opportunity to customer process."""

    name: str
    duration: timedelta
    conversion_rate: float = Field(..., ge=0, le=1)


class LeadConfig(BaseModel):
    stages: Tuple[LeadStage, ...]


# dynamically build the possible usage models options

predictor_pydantic_models: Dict[PredictorCategory, Tuple] = dict()

for predictor_category in PredictorCategory:
    predictors = list()

    for predictor_name in get_predictor_names(predictor_category):
        predictor_fn = get_predictor(predictor_category, predictor_name)
        parameters = inspect.signature(predictor_fn).parameters
        param_mapping = {
            p.name: (p.annotation, ...)
            for p in parameters.values()
            if (p.kind is inspect.Parameter.KEYWORD_ONLY or p.kind is inspect.Parameter.POSITIONAL_OR_KEYWORD)
            and (p.name not in ("state", "effective_date", "start"))
        }
        predictors.append(
            create_model(
                f"{predictor_category.name}__Predictor__{predictor_name}",
                __config__=BaseModel.Config,
                name=(str, Field(predictor_name, const=True)),
                **param_mapping,
            )
        )
    predictor_pydantic_models[predictor_category] = tuple(predictors)


class CustomerType(BaseModel):
    name: str
    monthly_fee: UFloat
    setup_fee: UFloat
    usage_fee: float
    usage_predictor: Union[predictor_pydantic_models[PredictorCategory.usage]]
    fraction_of_total_customers: float = Field(..., le=1, ge=0)
    cogs: "COGS"
    lead_config: LeadConfig


"""
Details of the team. Hires, costs, etc.
"""


class EmployeeCosts(BaseModel):
    # May want to take more detailed process from pylanner
    annual_fixed: float = 10000 + 3000  # Incl health insurance and other subscriptions
    annual_percent: float = 0.076 + 0.04


class Role(BaseModel):
    """High-level "role". Average sal and count level detail only."""

    name: str
    salary: float
    hire_predictor: Union[predictor_pydantic_models[PredictorCategory.headcount]]


class SalesRole(Role):
    """Extends `Role` to support commission compensation"""

    commission_percent: float = Field(..., ge=0, le=1)
    ramp_up_months: int
    monthly_quota: int


"""
Details of COGS
"""


class COGS(BaseModel):
    monthly: UFloat
    per_usage: UFloat


CustomerType.update_forward_refs()

"""
"Top-level" data. Generally provided as json etc. and predictions run based off of it.
"""


class Scenario(BaseModel):

    customer_types: Tuple[CustomerType, ...]
    headcount: Tuple[Union[SalesRole, Role], ...]
    employee_costs: EmployeeCosts = EmployeeCosts()

    @validator("customer_types")
    def customer_types_add_to_1(cls, v):
        fracs = [getattr(x, "fraction_of_total_customers") for x in v]
        if sum(fracs) != 1.0:
            raise ValueError(f"Total customer fractions must add to 1, not {sum(fracs)}")

        return v
