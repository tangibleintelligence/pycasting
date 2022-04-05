from pycasting.calc.predictors import predict, PredictorCategory
from pycasting.dataclasses.predictions import CustomerType
from pycasting.misc import MonthYear, UFloat


def estimate_usage(customer_type: CustomerType, start: MonthYear, effective: MonthYear) -> UFloat:
    """Estimates usage for this customer type"""
    usage_predictor = customer_type.usage_predictor
    params = usage_predictor.dict(exclude={"name"})
    return predict(PredictorCategory.usage, usage_predictor.name, effective.end_of_month, params, start.end_of_month)
