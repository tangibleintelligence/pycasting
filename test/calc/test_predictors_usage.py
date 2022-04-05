"""Tests usage modelling functions"""
from datetime import timedelta, datetime

from pycasting.calc.predictors import predict, PredictorCategory
from pycasting.misc import UFloat


def test_linear():
    rate_50 = UFloat(0.5, 0.1)
    rate_100 = UFloat(1, 0.15)
    initial_usage = UFloat(1200, 100)

    start = datetime.now().date()

    # 50%, 3 months later
    params = {"initial_usage": initial_usage, "increase_per_year": rate_50}
    u = predict(PredictorCategory.usage, "linear", start + timedelta(days=90), params, start=start)
    assert u.n == 1350

    # 100%, @ start
    params = {"initial_usage": initial_usage, "increase_per_year": rate_100}
    u = predict(PredictorCategory.usage, "linear", start, params, start=start)
    assert u.n == 1200
    assert u.s == initial_usage.s

    # # 100%, 6 months later
    u = predict(PredictorCategory.usage, "linear", start + timedelta(days=180), params, start=start)
    assert u.n == 1800

    # # 100%, 1 year later
    u = predict(PredictorCategory.usage, "linear", start + timedelta(days=360), params, start=start)
    assert u.n == 2400
    assert u.s > initial_usage.s * 2
