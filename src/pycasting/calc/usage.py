from pycasting.calc.customers import customer_ages
from pycasting.calc.predictors import predict, PredictorCategory
from pycasting.pydanticmodels.actuals import Actuals
from pycasting.pydanticmodels.predictions import CustomerType, Scenario
from pycasting.misc import MonthYear, UFloat


def estimate_usage(customer_type: CustomerType, start: MonthYear, effective: MonthYear) -> UFloat:
    """Estimates usage for this customer type"""
    usage_predictor = customer_type.usage_predictor
    params = usage_predictor.dict(exclude={"name"})
    return predict(PredictorCategory.usage, usage_predictor.name, effective.end_of_month, params, start.end_of_month)


def estimate_total_usage(scenario: Scenario, actuals: Actuals, effective: MonthYear, customer_type: CustomerType):
    """Estimate total usage in given month for given customer type"""
    return sum(
        estimate_usage(customer_type, customer_start, effective)
        for customer_start, count in customer_ages(scenario, actuals, effective, customer_type).items()
    )
