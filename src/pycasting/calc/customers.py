"""
Calculation of customers...totals etc.
"""
from functools import lru_cache

from pycasting.calc.sales import new_transitions
from pycasting.dataclasses.actuals import Actuals
from pycasting.dataclasses.predictions import Scenario, CustomerType
from pycasting.misc import MonthYear


@lru_cache
def new_customers(scenario: Scenario, month_year: MonthYear, customer_type: CustomerType) -> int:
    """New customers of a given type in a given month"""
    return new_transitions(scenario, month_year, None, customer_type)


@lru_cache
def churned_customers(scenario: Scenario, actuals: Actuals, month_year: MonthYear, customer_type: CustomerType) -> int:
    """Customers of a given type who leave in a given month."""
    return round(customer_type.churn * total_customers(scenario, actuals, month_year.shift_month(-1), customer_type))


@lru_cache
def total_customers(scenario: Scenario, actuals: Actuals, month_year: MonthYear, customer_type: CustomerType) -> int:
    """Total customers at end of the given month."""
    if month_year < actuals.first_unknown_month_year:
        return actuals.active_customers[customer_type.name]

    # Starting with the actual # of customers and actuals accurate_as_of date, simulate starting and churning customers
    # each month.
    customer_count: int = actuals.active_customers[customer_type.name]

    for my in MonthYear.between(actuals.first_unknown_month_year, month_year):
        # Customers join ...
        customer_count += new_customers(scenario, my, customer_type)

        # ...and they churn
        customer_count -= churned_customers(scenario, actuals, my, customer_type)

    return customer_count
