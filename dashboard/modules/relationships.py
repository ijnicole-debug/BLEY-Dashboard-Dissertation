from shiny import ui, render
from shinywidgets import output_widget, render_plotly

import pandas as pd
import plotly.express as px


# =====================================================
# Friendly Variable Names
# =====================================================

VARIABLES = {

    "gld": "Good Level of Development (GLD)",
    "fsm": "Free School Meals (FSM)",
    "sen": "Special Educational Needs (SEN)",
    "idaci": "Income Deprivation (IDACI)",
    "ofsted": "Average Ofsted Rating",
    "total_places": "Childcare Places",
    "under5": "Under-5 Population",
    "childcare_per_100": "Childcare Places per 100 Children",
    "ethnic_diversity": "Ethnic Diversity"

}


# =====================================================
# Relationships Page
# =====================================================

def relationships_page(summary):

    return ui.nav_panel(

        "📈 Relationships",

        ui.h2("Relationships Between Educational Factors"),

        ui.p(
            """
            Explore how educational and socioeconomic factors
            are related across London's 32 boroughs.

            Each point on the chart represents one borough.
            The trend line summarises the overall relationship
            between the selected variables.
            """
        ),

        ui.layout_columns(

            ui.input_select(

                "x_variable",

                "Compare this factor",

                choices=VARIABLES,

                selected="fsm"

            ),

            ui.input_select(

                "y_variable",

                "Against this factor",

                choices=VARIABLES,

                selected="gld"

            ),

            col_widths=(6,6)

        ),

        ui.hr(),

        output_widget("relationship_chart"),

        ui.hr(),

        ui.h3("Relationship Summary"),

        ui.output_table("relationship_summary"),

        ui.hr(),

        ui.h3("What does this mean?"),

        ui.output_text_verbatim("relationship_interpretation")

    )


# =====================================================
# Relationships Server
# =====================================================

def relationships_server(input, output, session, summary):

    df = summary["df"]

    @render_plotly
    def relationship_chart():

        x = input.x_variable()
        y = input.y_variable()

        fig = px.scatter(

            df,

            x=x,

            y=y,

            text="borough",

            trendline="ols",

            color=y,

            color_continuous_scale="Viridis",

            labels={
                x: VARIABLES[x],
                y: VARIABLES[y]
            }

        )

        fig.update_traces(

            textposition="top center"

        )

        fig.update_layout(

            height=650,

            showlegend=False,

            plot_bgcolor="white",

            paper_bgcolor="white"

        )

        return fig


    @render.table
    def relationship_summary():

        x = input.x_variable()
        y = input.y_variable()

        corr = df[x].corr(df[y])

        if abs(corr) >= 0.70:
            strength = "Strong"

        elif abs(corr) >= 0.50:
            strength = "Moderate"

        elif abs(corr) >= 0.30:
            strength = "Weak"

        else:
            strength = "Very Weak"

        summary_df = pd.DataFrame({

            "Measure": [

                "Correlation",

                "Relationship Strength",

                "Average " + VARIABLES[x],

                "Average " + VARIABLES[y],

                "Number of Boroughs"

            ],

            "Value": [

                round(corr,2),

                strength,

                round(df[x].mean(),2),

                round(df[y].mean(),2),

                len(df)

            ]

        })

        return summary_df


    @render.text
    def relationship_interpretation():

        x = input.x_variable()
        y = input.y_variable()

        corr = df[x].corr(df[y])

        if corr > 0.7:

            return f"""
There is a strong positive relationship between
{VARIABLES[x]} and {VARIABLES[y]}.

This means that boroughs with higher values of
{VARIABLES[x]} also tend to have higher values of
{VARIABLES[y]}.
"""

        elif corr > 0.3:

            return f"""
There is a moderate positive relationship between
{VARIABLES[x]} and {VARIABLES[y]}.

As {VARIABLES[x]} increases,
{VARIABLES[y]} generally increases,
although there are exceptions.
"""

        elif corr < -0.7:

            return f"""
There is a strong negative relationship between
{VARIABLES[x]} and {VARIABLES[y]}.

As {VARIABLES[x]} increases,
{VARIABLES[y]} generally decreases.
"""

        elif corr < -0.3:

            return f"""
There is a moderate negative relationship between
{VARIABLES[x]} and {VARIABLES[y]}.

Higher values of {VARIABLES[x]}
are generally associated with lower values of
{VARIABLES[y]}.
"""

        else:

            return f"""
There is little evidence of a strong relationship
between {VARIABLES[x]} and {VARIABLES[y]}.

This suggests that changes in one variable
do not consistently predict changes in the other.
"""