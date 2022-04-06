from clearcut import get_logger

from pycasting.calc.customers import total_customers
from pycasting.dataclasses.predictions import Scenario
from pycasting.misc import MonthYear

logger = get_logger(__name__)


def test_customer_timeline(salesperson_role, simple_customer_type, actuals, rent):
    scenario = Scenario(
        customer_types=(simple_customer_type,),
        headcount=(salesperson_role,),
        misc_bizdev_expenses=tuple(),
        misc_expenses=(rent,)
    )

    assert total_customers(scenario, actuals, MonthYear.from_date(actuals.accurate_as_of), simple_customer_type) == 0

    # Not asserting, just printing for sanity checks
    for shift in range(1, 12):
        logger.info(f"{shift} months in future:")
        total = total_customers(scenario, actuals, MonthYear.from_date(actuals.accurate_as_of).shift_month(shift), simple_customer_type)
        logger.info(f"Total customers: {total}")
