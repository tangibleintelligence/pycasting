"""
Runs forecasting.
Run this app with `python app.py` and visit http://127.0.0.1:8050/ in your web browser.
"""
import json
from pathlib import Path

import altair as alt
import streamlit as st
import typer
from frozendict import frozendict
from numerize.numerize import numerize

from pycasting.calc.cashflow import monthly_revenue, monthly_expenses
from pycasting.calc.customers import new_customers
from pycasting.calc.forecasting import forecast
from pycasting.pydanticmodels.actuals import Actuals
from pycasting.pydanticmodels.predictions import Scenario

cli = typer.Typer()


@cli.command()
def main(scenario: Path, months_ahead: int = 18):
    # TODO read actuals
    actuals = Actuals(cash_on_hand=210_000, active_customers=frozendict({"Small - Seat Based": 1}))

    # Read Scenario
    with open(scenario, "r") as f:
        data = json.load(f)

    scenario_obj = Scenario(**data)

    # Run forecast
    df = forecast(scenario_obj, actuals, months_ahead)

    # Build dashboard layout via streamlit
    st.set_page_config(layout="wide")
    st.title("Tangible Intelligence Forecasting")

    # Graphs
    eom_date_x = alt.X("yearmonth(eom_date)", title="Month/Year")
    cashflow_y = alt.Y("cashflow", title="Cash Flow")
    cashflow_stddev = alt.YError("cashflow_stddev", title="Error")
    cash_on_hand_y = alt.Y("cash_on_hand", title="Cash on Hand")
    cash_on_hand_stddev = alt.YError("cash_on_hand_stddev", title="Error")
    revenue_y = alt.Y("revenue", title="MRR")
    revenue_stddev = alt.YError("revenue_stddev", title="Error")

    cashflow = alt.Chart(df).mark_line().encode(x=eom_date_x, y=cashflow_y)
    cashflow += alt.Chart(df).mark_errorband().encode(x=eom_date_x, y=cashflow_y, yError=cashflow_stddev)

    cash_on_hand = alt.Chart(df).mark_line().encode(x=eom_date_x, y=cash_on_hand_y)
    cash_on_hand += alt.Chart(df).mark_errorband().encode(x=eom_date_x, y=cash_on_hand_y, yError=cash_on_hand_stddev)

    revenue = alt.Chart(df).mark_line().encode(x=eom_date_x, y=revenue_y)
    revenue += alt.Chart(df).mark_errorband().encode(x=eom_date_x, y=revenue_y, yError=revenue_stddev)

    # Display it all

    col1, col2, col3 = st.columns(3)
    months_18 = actuals.first_unknown_month_year.shift_month(18)
    mrr_18_months = monthly_revenue(scenario_obj, actuals, months_18, None)

    new_customers_18_months = new_customers(scenario_obj, months_18, None)

    cac_18_months = monthly_expenses(scenario_obj, actuals, months_18)[1] / new_customers_18_months

    col1.metric("MRR @ 18 months", f"${numerize(mrr_18_months.nominal_value)}")
    col2.metric("CaC @ 18 months", f"${numerize(cac_18_months.nominal_value)}")
    col3.metric("Monthly new customers @ 18 months", f"{numerize(new_customers_18_months)}")

    col1, col2 = st.columns(2)
    col1.altair_chart(revenue, use_container_width=True)
    col2.altair_chart(cashflow, use_container_width=True)

    st.subheader("More Info")
    with st.expander("Accounting"):
        st.altair_chart(cash_on_hand, use_container_width=True)
    with st.expander("Raw details"):
        st.write(df)
    with st.expander("Show scenario json"):
        st.json(data)

    #
    # fig = px.line(df, x="eom_date", y="cashflow", error_y="cashflow_stddev")
    #
    # # Layout
    # app.layout = html.Div(children=[
    #     html.H1(children='Hello Dash'),
    #
    #     html.Div(children='''
    #     Dash: A web application framework for your data.
    # '''),
    #
    #     dcc.Graph(
    #         id='example-graph',
    #         figure=fig
    #     )
    # ])
    #
    # # Run
    # app.run_server(debug=True)


if __name__ == "__main__":
    cli(standalone_mode=False)
