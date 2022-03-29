"""Tests usage modelling functions"""
from datetime import timedelta

from pycasting.modeling import usage
from pycasting.modeling.misc import UFloat


def test_linear():
    rate_50 = UFloat(0.5, 0.1)
    rate_100 = UFloat(1, 0.15)
    initial_usage = UFloat(1000, 100)

    # 50%, 2 months later
    u = usage.linear(initial_usage, timedelta(days=60), rate_per_30_days=rate_50)
    assert u.n == 2000

    # 100%, 0 months later
    u = usage.linear(initial_usage, timedelta(days=0), rate_per_30_days=rate_100)
    assert u.n == 1000
    assert u.s == initial_usage.s

    # # 100%, 1 months later
    u = usage.linear(initial_usage, timedelta(days=30), rate_per_30_days=rate_100)
    assert u.n == 2000

    # # 100%, 1.5 months later
    u = usage.linear(initial_usage, timedelta(days=45), rate_per_30_days=rate_100)
    assert u.n == 2500

    # # 100%, 2 months later
    u = usage.linear(initial_usage, timedelta(days=60), rate_per_30_days=rate_100)
    assert u.n == 3000

    # # 100%, 3 months later
    u = usage.linear(initial_usage, timedelta(days=90), rate_per_30_days=rate_100)
    assert u.n == 4000
    assert u.s > initial_usage.s * 4
