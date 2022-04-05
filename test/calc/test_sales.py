from clearcut import get_logger

from pycasting.calc.sales import new_transitions
from pycasting.dataclasses.predictions import Scenario
from pycasting.misc import MonthYear

logger = get_logger(__name__)


def test_transitions(salesperson_role, salesperson_hire_predictor, simple_customer_type, initial_lead_stage, close_lead_stage):

    scenario = Scenario(
        customer_types=(simple_customer_type,),
        headcount=(salesperson_role,),
    )

    # before hiring salespeople, should be nothing
    effective_month_year = MonthYear.from_date(salesperson_hire_predictor.first_hire_date).shift_month(-1)
    assert new_transitions(scenario, effective_month_year, initial_lead_stage, simple_customer_type) == 0
    assert new_transitions(scenario, effective_month_year, close_lead_stage, simple_customer_type) == 0

    # Few other situations. Not testing, just used to run through code in debug mode.
    for shift in range(1, 6):
        logger.info(f"{shift} months in future:")
        logger.info(
            f"Initial: {new_transitions(scenario, effective_month_year.shift_month(shift), initial_lead_stage, simple_customer_type)}"
        )
        logger.info(f"Close: {new_transitions(scenario, effective_month_year.shift_month(shift), close_lead_stage, simple_customer_type)}")
