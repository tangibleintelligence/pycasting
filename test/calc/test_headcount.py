"""
Tests headcount calculators
"""
from datetime import timedelta

from dateutil.relativedelta import relativedelta

from pycasting.calc.headcount import hires_through_effective_date, hires_in_month
from pycasting.misc import MonthYear, end_of_month


def test_linear_sales_hires(salesperson_hire_predictor, salesperson_role):
    # no one before
    effective_date = salesperson_hire_predictor.first_hire_date - relativedelta(days=1)
    assert hires_through_effective_date(effective_date, salesperson_role) == 0

    effective_date = salesperson_hire_predictor.first_hire_date - relativedelta(months=1)
    assert hires_in_month(MonthYear.from_date(effective_date), salesperson_role) == 0

    # First hire on date

    effective_date = salesperson_hire_predictor.first_hire_date
    assert hires_through_effective_date(effective_date, salesperson_role) == 1

    # By end of the month, everyone should have been hired this month
    effective_date = end_of_month(effective_date)
    hires_by_eom = hires_through_effective_date(effective_date, salesperson_role)
    assert hires_in_month(MonthYear.from_date(effective_date), salesperson_role) == hires_by_eom

    # 6 hires within 6 months
    hires_in_6_months = salesperson_hire_predictor.hires_per_year // 2
    effective_date = salesperson_hire_predictor.first_hire_date + timedelta(days=360 // 2 - 1)  # 6 months with our 360-day year
    assert hires_through_effective_date(effective_date, salesperson_role) == hires_in_6_months

    # 10 hires after a year (bc of cap)
    max_hires = salesperson_hire_predictor.max_hires
    effective_date = salesperson_hire_predictor.first_hire_date + relativedelta(months=12)
    assert hires_through_effective_date(effective_date, salesperson_role) == max_hires

    # Add each month up
    total_hires = 0
    month_year = MonthYear.from_date(salesperson_hire_predictor.first_hire_date)
    while month_year.end_of_month <= effective_date:
        total_hires += hires_in_month(month_year, salesperson_role)
        month_year = month_year.shift_month(1)

    assert total_hires == max_hires
