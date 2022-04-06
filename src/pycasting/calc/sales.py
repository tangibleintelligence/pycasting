"""
Sales forecasting logic. Predicting the future...ooooaaaaa
"""
import math
from functools import lru_cache
from typing import Optional

from pycasting.calc.headcount import hires_through_effective_date, hires_in_month
from pycasting.pydanticmodels.predictions import Scenario, LeadStage, SalesRole, CustomerType
from pycasting.misc import MonthYear


@lru_cache
def total_sales_quota(scenario: Scenario, month_year: MonthYear) -> float:
    """
    Calculate the total sales quota for this MonthYear. Uses the number of "effective sales reps" at the end of this MonthYear,
    which is based on number hired, incorporating the fact that new sales reps take some time to "ramp up" to max effectiveness.
    """

    quota = 0

    for sales_role in scenario.headcount:
        if not isinstance(sales_role, SalesRole):
            continue

        effective_sales_reps = 0

        # role defines a ramp up time. Go back that many months and everyone hired up to then is fully effective
        # Then get anyone hired after that and "prorate" their effectiveness accordingly
        ramp_up_months = sales_role.ramp_up_months
        effectiveness_increase_per_month = 1 / ramp_up_months

        # Fully effective reps...who was hired by the end of the month ramp_up ago? (Because they would be considered fully ramped
        # up by this month_year.
        effective_sales_reps += hires_through_effective_date(month_year.shift_month(-sales_role.ramp_up_months).end_of_month, sales_role)

        # Less effective reps we need to add in one month at a time. We care about this month (0) up to ramp_up - 1.
        for months_ago in range(0, ramp_up_months):
            # who was hired within the month `months_ago`?
            num_hires = hires_in_month(month_year.shift_month(-months_ago), sales_role)
            # Those folks are partially effective. They increase at a rate per month, including the month in question.
            effectiveness = effectiveness_increase_per_month * (1 + months_ago)
            # Add this cohort in
            effective_sales_reps += num_hires * effectiveness

        # This effective number of sales reps should handle a quota of work
        # In the Senovo spreadsheet, they have a monthly quota for all sales roles.
        quota += sales_role.monthly_quota * effective_sales_reps

    return quota


@lru_cache
def new_transitions(scenario: Scenario, month_year: MonthYear, stage: Optional[LeadStage], customer_type: CustomerType) -> int:
    """
    Predict the number of transitions into a given stage + customer type in a given month/year.
    """

    # This modelling is roughly based on the Senovo B2B SaaS Excel. I'm not confident that only including sales "effectiveness" on the
    # initial transition is a good idea, but that's how they do it so I'm going to replicate for the like-for-like transition.

    if stage is not None and customer_type.lead_config.stages[0] == stage:
        # If we're at the first stage, the transitions into it are the lead quota per rep * number of "effective reps" for each sales role
        # type. An "effective rep" is based on how many reps are available, given that they ramp up over some period of time.
        return round(total_sales_quota(scenario, month_year))
    else:
        # See https://tangibleintelligence.slab.com/posts/sales-progression-logic-o1rjhcag for this logic. It's based on the Senovo
        # spreadsheet, but is a little more accurate.
        if stage is None:
            previous_stages = customer_type.lead_config.stages
        else:
            current_stage_index = customer_type.lead_config.stages.index(stage)
            previous_stages = customer_type.lead_config.stages[0:current_stage_index]

        # How long has it been since stage 0? (Called Delta in the Slab page.)
        duration_since_stage_0 = math.floor(sum(s.duration.total_seconds() / 24 / 60 / 60 for s in previous_stages))
        # Break into months and days (`mu` and `delta` on Slab)
        months: int
        days: int
        months, days = divmod(duration_since_stage_0, 30)

        # And what's the net conversion rate since stage 0? (Called capital Chi in slab page.)
        net_conversion_rate_since_stage_0 = math.prod(s.conversion_rate for s in previous_stages)

        # Transitions in this month is going to come in two parts. Some from `months` ago, and some from `months + 1` ago (sigma_`tau`
        # in slab). Ratio of those two sources is based on `days`. See slab page for full equation.

        # First get the number of transitions into stage 0 `months` ago and `months + 1` ago. Recursive!
        transitions_per_day_months_ago = (
            new_transitions(scenario, month_year.shift_month(-months), customer_type.lead_config.stages[0], customer_type) / 30
        )
        transitions_per_day_months_plus_one_ago = (
            new_transitions(scenario, month_year.shift_month(-(months + 1)), customer_type.lead_config.stages[0], customer_type) / 30
        )

        # Add in proportion
        proportional_transitions = days * transitions_per_day_months_plus_one_ago + (30 - days) * transitions_per_day_months_ago

        # And multiply by net conversion rate

        return round(net_conversion_rate_since_stage_0 * proportional_transitions)
