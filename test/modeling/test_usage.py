"""Tests usage modelling functions"""
from datetime import timedelta, date, datetime

from pycasting.dataclasses_actuals import Actuals
from pycasting.misc import UFloat
from pycasting.predictors import get_predictor, PredictorCategory, PredictedCompanyState


def test_linear():
    rate_50 = UFloat(0.5, 0.1)
    rate_100 = UFloat(1, 0.15)
    initial_usage = UFloat(1200, 100)

    actuals = Actuals(accurate_as_of=date(2000, 1, 1))
    start = datetime.now().date()

    usage_linear = get_predictor(PredictorCategory.usage, "linear")

    # 50%, 3 months later
    state = PredictedCompanyState(actuals=actuals, effective_date=start + timedelta(days=90), number_of_customers=0)
    u = usage_linear(state, start, initial_usage=initial_usage, increase_per_year=rate_50)
    assert u.n == 1350

    # 100%, @ start
    state = PredictedCompanyState(actuals=actuals, effective_date=start, number_of_customers=0)
    u = usage_linear(state, start, initial_usage=initial_usage, increase_per_year=rate_100)
    assert u.n == 1200
    assert u.s == initial_usage.s

    # # 100%, 6 months later
    state = PredictedCompanyState(actuals=actuals, effective_date=start + timedelta(days=180), number_of_customers=0)
    u = usage_linear(state, start, initial_usage=initial_usage, increase_per_year=rate_100)
    assert u.n == 1800

    # # 100%, 1 year later
    state = PredictedCompanyState(actuals=actuals, effective_date=start + timedelta(days=360), number_of_customers=0)
    u = usage_linear(state, start, initial_usage=initial_usage, increase_per_year=rate_100)
    assert u.n == 2400
    assert u.s > initial_usage.s * 2
