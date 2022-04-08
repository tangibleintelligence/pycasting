"""
Cashflow calculations. Incoming, outgoing, reserves.
"""
from functools import lru_cache
from typing import Optional, Tuple

from pycasting.calc.customers import new_customers, total_customers, customer_ages
from pycasting.calc.headcount import hires_through_effective_date
from pycasting.calc.predictors import PredictedCompanyState
from pycasting.calc.sales import new_transitions
from pycasting.calc.usage import estimate_usage, estimate_total_usage
from pycasting.pydanticmodels.actuals import Actuals
from pycasting.pydanticmodels.predictions import CustomerType, Scenario
from pycasting.misc import MonthYear, UFloat


@lru_cache
def monthly_revenue(scenario: Scenario, actuals: Actuals, effective_month_year: MonthYear, customer_type: Optional[CustomerType]) -> UFloat:
    """Calculate income from given customer type (or all customers)"""
    income = UFloat(0, 0)
    if customer_type is None:
        return sum(monthly_revenue(scenario, actuals, effective_month_year, ct) for ct in scenario.customer_types)
    else:
        # We'll be collecting a certain number of months behind
        effective_month_year = effective_month_year.shift_month(-customer_type.payment_months_behind)

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
            income += expected_usage * customer_type.usage_fee * count

        return income


def monthly_expenses(scenario: Scenario, actuals: Actuals, effective_month_year: MonthYear) -> Tuple[UFloat, UFloat]:
    """Calculate expenses for a month. Returns tuple of (total expenses, CAC expenses)"""
    expenses = UFloat(0, 0)
    cac_expenses = UFloat(0, 0)

    state: PredictedCompanyState = PredictedCompanyState(
        number_of_customers=total_customers(scenario, actuals, effective_month_year, None), actuals=actuals
    )

    # Marketing
    for customer_type in scenario.customer_types:
        # Marketing spend = cpc * clicks = cpc * (new_leads / (qualified lead to click ratio))
        cpc = customer_type.lead_config.cost_per_ad_click
        new_qualified_leads = new_transitions(scenario, effective_month_year, customer_type.lead_config.stages[0], customer_type)
        lead_to_click_ratio = customer_type.lead_config.qualified_lead_to_click_ratio
        marketing_expenses = cpc * new_qualified_leads / lead_to_click_ratio

        expenses += marketing_expenses
        cac_expenses += marketing_expenses

    # Salaries etc.
    for role in scenario.headcount:
        role_cost = (
            role.monthly_salary + (role.monthly_salary * scenario.employee_costs.annual_percent + scenario.employee_costs.annual_fixed) / 12
        )
        total_role_cost = role_cost * hires_through_effective_date(effective_month_year.end_of_month, role, state)
        expenses += total_role_cost

        if role.customer_acquisition:
            cac_expenses += total_role_cost

    # COGS
    for customer_type in scenario.customer_types:
        monthly_usage = estimate_total_usage(scenario, actuals, effective_month_year, customer_type)
        expenses += customer_type.cogs.monthly + customer_type.cogs.per_usage * monthly_usage

    # Other spend
    for exp in scenario.misc_expenses:
        expenses += exp.monthly

    for exp in scenario.misc_bizdev_expenses:
        expenses += exp.monthly
        cac_expenses += exp.monthly

    return expenses, cac_expenses
