from shiny import ui, render
from shinywidgets import output_widget, render_plotly

import pandas as pd
import plotly.express as px


# =====================================================
# Relationships Page
# =====================================================

def relationships_page(summary):

    variable_choices = [

        "gld",
        "fsm",
        "sen",
        "idaci",
        "ofsted",
        "total_places",
        "under5",
        "childcare_per_100",
        "ethnic_diversity"

    ]

    return ui.nav_panel(

        "📈 Relationships",

        ui.h2("Relationships Between Variables"),

        ui.p(
            """
            Explore the relationships between educational
            attainment and socioeconomic indicators across
            London boroughs.
            """
        ),

        ui.layout_columns(

            ui.input_select(

                "x_variable",

                "Select X Variable",

                choices=variable_choices,

                selected="fsm"

            ),

            ui.input_select(

                "y_variable",

                "Select Y Variable",

                choices=variable_choices,

                selected="gld"

            ),

            col_widths=(6,6)

        ),

        ui.hr(),

        output_widget("relationship_chart"),

        ui.hr(),

        ui.h3("Summary Statistics"),

        ui.output_table("relationship_summary")

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

            color_continuous_scale="Blues"

        )

        fig.update_traces(

            textposition="top center"

        )

        fig.update_layout(

            height=600,

            plot_bgcolor="white",

            paper_bgcolor="white",

            title=None

        )

        return fig


    @render.table
    def relationship_summary():

        x = input.x_variable()
        y = input.y_variable()

        summary_df = pd.DataFrame({

            "Statistic": [

                "X Variable Mean",

                "Y Variable Mean",

                "Number of Boroughs"

            ],

            "Value": [

                round(df[x].mean(),1),

                round(df[y].mean(),1),

                len(df)

            ]

        })

        return summary_df
