from clearcut import get_logger

from pycasting.calc.cashflow import monthly_revenue, monthly_expenses
from pycasting.pydanticmodels.predictions import Scenario
from pycasting.misc import MonthYear

logger = get_logger(__name__)


def test_monthly_income(simple_customer_type, salesperson_role, actuals):
    """Just for running and checking interactively"""
    scenario = Scenario(
        customer_types=(simple_customer_type,),
        headcount=(salesperson_role,),
        misc_expenses=tuple(),
        misc_bizdev_expenses=tuple(),
    )

    assert monthly_revenue(scenario, actuals, MonthYear.from_date(actuals.accurate_as_of), simple_customer_type) == 0

    # Not asserting, just printing for sanity checks
    for shift in range(1, 12):
        logger.info(f"{shift} months in future:")
        total = monthly_revenue(scenario, actuals, MonthYear.from_date(actuals.accurate_as_of).shift_month(shift), simple_customer_type)
        logger.info(f"Total monthly income: {total}")


def test_monthly_expenses(simple_customer_type, salesperson_role, actuals, rent):
    """Just for running and checking interactively"""
    scenario = Scenario(
        customer_types=(simple_customer_type,),
        headcount=(salesperson_role,),
        misc_expenses=(rent,),
        misc_bizdev_expenses=tuple(),
    )

    # Not asserting, just printing for sanity checks
    for shift in range(0, 12):
        logger.info(f"{shift} months in future:")
        total = monthly_expenses(scenario, actuals, MonthYear.from_date(actuals.accurate_as_of).shift_month(shift))
        logger.info(f"Total monthly expenses: {total}")
