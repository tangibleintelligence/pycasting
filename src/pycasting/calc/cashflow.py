"""
Cashflow calculations. Incoming, outgoing, reserves.
"""
from typing import Optional

from pycasting.calc.customers import new_customers, total_customers, customer_ages
from pycasting.calc.usage import estimate_usage
from pycasting.dataclasses.actuals import Actuals
from pycasting.dataclasses.predictions import CustomerType, Scenario
from pycasting.misc import MonthYear, UFloat


def monthly_income(scenario: Scenario, actuals: Actuals, effective_month_year: MonthYear, customer_type: Optional[CustomerType]) -> UFloat:
    """Calculate income from given customer type (or all customers)"""
    income = UFloat(0, 0)
    if customer_type is None:
        return sum(monthly_income(scenario, actuals, effective_month_year, ct) for ct in scenario.customer_types)
    else:
        # Setup fee for new customers
        new_customer_count = new_customers(scenario, effective_month_year, customer_type)
        income += new_customer_count * customer_type.setup_fee

        # Monthly fee for all customers
        total_customer_count = total_customers(scenario, actuals, effective_month_year, customer_type)
        income += total_customer_count * customer_type.monthly_fee

        # Expected usage
        for customer_start, count in customer_ages(scenario, actuals, effective_month_year, customer_type).items():
            # usage at this point in time?
            expected_usage: UFloat = estimate_usage(customer_type, customer_start, effective_month_year)

            # Charge them
            income += expected_usage * customer_type.usage_fee

        return income
