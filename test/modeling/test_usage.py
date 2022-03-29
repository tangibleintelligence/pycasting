"""Tests usage modelling functions"""
from datetime import timedelta

from pycasting.predicting import usage
from pycasting.predicting.misc import UFloat


def test_linear():
    rate_50 = UFloat(0.5, 0.1)
    rate_100 = UFloat(1, 0.15)
    initial_usage = UFloat(1200, 100)

    # 50%, 3 months later
    u = usage.linear(timedelta(days=90), initial_usage=initial_usage, increase_per_year=rate_50)
    assert u.n == 1350

    # 100%, 0 months later
    u = usage.linear(timedelta(days=0), initial_usage=initial_usage, increase_per_year=rate_100)
    assert u.n == 1200
    assert u.s == initial_usage.s

    # # 100%, 6 months later
    u = usage.linear(timedelta(days=180), initial_usage=initial_usage, increase_per_year=rate_100)
    assert u.n == 1800

    # # 100%, 1 year later
    u = usage.linear(timedelta(days=360), initial_usage=initial_usage, increase_per_year=rate_100)
    assert u.n == 2400
    assert u.s > initial_usage.s * 2
