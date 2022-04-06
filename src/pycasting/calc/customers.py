"""
Calculation of customers...totals etc.
"""
from collections import Counter
from functools import lru_cache
from typing import Dict, Optional

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
def total_customers(scenario: Scenario, actuals: Actuals, month_year: MonthYear, customer_type: Optional[CustomerType]) -> int:
    """Total customers at end of the given month."""
    if customer_type is None:
        return sum(total_customers(scenario, actuals, month_year, ct) for ct in scenario.customer_types)

    if month_year < actuals.first_unknown_month_year:
        return actuals.active_customers[customer_type.name]
    else:
        return customer_ages(scenario, actuals, month_year, customer_type).total()


@lru_cache
def customer_ages(scenario: Scenario, actuals: Actuals, month_year: MonthYear, customer_type: CustomerType) -> Counter[MonthYear]:
    """Returns the distribution of customer ages...a mapping of customer start to # of customers who started in that month."""
    # This is a similar problem to apportionment, interestingly.
    if month_year < actuals.first_unknown_month_year:
        return Counter()

    # Starting with the actual # of customers and actuals accurate_as_of date, simulate starting and churning customers
    # each month.
    customers: Counter[MonthYear] = Counter()

    for my in MonthYear.between(actuals.first_unknown_month_year, month_year):
        # Customers join, this month
        customers.update({my: new_customers(scenario, my, customer_type)})

        # ...and they churn, since the beginning.
        # TODO split out to churn predictor
        # For now, we assume a simple churning formula. All customers have an equal chance of churning.
        # So, for each month, the churned count is
        # (% of customers in that month bucket) * (total expected churn this month)
        # == customers in month * churn %

        churn_counts: Dict[MonthYear, int] = {k: round(v * customer_type.churn) for k, v in customers.items()}
        customers.subtract(churn_counts)

    return customers
