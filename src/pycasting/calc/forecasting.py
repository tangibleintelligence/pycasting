"""
Top-level forecasting and collection logic. Outputs data etc. to be dashboarded
"""
import math
from typing import Dict

import pandas as pd

from pycasting.calc.cashflow import monthly_revenue, monthly_expenses
from pycasting.misc import MonthYear, UFloat
from pycasting.pydanticmodels.actuals import Actuals
from pycasting.pydanticmodels.predictions import Scenario


def forecast(scenario: Scenario, actuals: Actuals, months_ahead: int):
    """
    Generate forecast in dataframe format.
    """

    data = list()

    cash_on_hand: UFloat = UFloat(actuals.cash_on_hand, 0)

    for shift in range(0, months_ahead):
        month_year = MonthYear.from_date(actuals.accurate_as_of).shift_month(shift)

        rev_per_customer: Dict[str, UFloat] = {
            ct.name: monthly_revenue(scenario, actuals, month_year, ct) for ct in scenario.customer_types
        }
        rev: UFloat = sum(rev_per_customer.values())
        exp, cac_exp = monthly_expenses(scenario, actuals, month_year)

        cash_on_hand = cash_on_hand + rev - exp

        row = {
            "month": month_year.month,
            "year": month_year.year,
            "month_year": repr(month_year),
            "eom_date": month_year.end_of_month,
            "revenue": rev.nominal_value,
            "revenue_stddev": rev.std_dev,
            "expenses": exp.nominal_value,
            "expenses_stddev": exp.std_dev,
            "cac_expenses": cac_exp.nominal_value,
            "cac_expenses_stddev": cac_exp.std_dev,
            "cashflow": (rev - exp).nominal_value,
            "cashflow_stddev": (rev - exp).std_dev,
            "cash_on_hand": cash_on_hand.nominal_value,
            "cash_on_hand_stddev": cash_on_hand.std_dev,
        }

        row.update({f"revenue__{k}": v.n for k, v in rev_per_customer.items()})
        row.update({f"revenue_stddev__{k}": v.s for k, v in rev_per_customer.items()})

        data.append(row)

    return pd.DataFrame(data)
