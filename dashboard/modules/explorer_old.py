from shiny import ui, render
from shinywidgets import output_widget, render_plotly

import pandas as pd
import plotly.express as px


# =====================================================
# Borough Explorer Page
# =====================================================

def explorer_page(summary):

    boroughs = sorted(summary["df"]["borough"].tolist())

    return ui.nav_panel(

        "📊 Borough Explorer",

        ui.h2("Borough Explorer"),

        ui.p(
            """
            Select a London borough to explore its educational
            attainment and socioeconomic indicators.
            """
        ),

        ui.input_select(

            "borough",

            "Select Borough",

            choices=boroughs,

            selected=boroughs[0]

        ),

        ui.hr(),

        ui.layout_columns(

            ui.card(

                ui.card_header("Borough Statistics"),

                ui.output_table("borough_profile")

            ),

            ui.card(

                ui.card_header("GLD Comparison"),

                output_widget("borough_gld_chart")

            ),

            col_widths=(5,7)

        )

    )

# Borough Explorer Server


def explorer_server(input, output, session, summary):

    df = summary["df"]

    @render.table
    def borough_profile():

        borough = input.borough()

        row = df[df["borough"] == borough].iloc[0]

        profile = pd.DataFrame({

            "Metric": [

                "Good Level of Development (%)",

                "Free School Meals (%)",

                "Special Educational Needs (%)",

                "IDACI",

                "Ofsted",

                "Total Places",

                "Under 5 Population",

                "Childcare per 100",

                "Ethnic Diversity"

            ],

            "Value": [

                round(row["gld"],1),

                round(row["fsm"],1),

                round(row["sen"],1),

                round(row["idaci"],1),

                round(row["ofsted"],1),

                int(row["total_places"]),

                int(row["under5"]),

                round(row["childcare_per_100"],1),

                round(row["ethnic_diversity"],1)

            ]

        })

        return profile


    @render_plotly
    def borough_gld_chart():

        borough = input.borough()

        borough_gld = df.loc[
            df["borough"] == borough,
            "gld"
        ].iloc[0]

        comparison = pd.DataFrame({

            "Category": [

                borough,

                "London Average"

            ],

            "GLD": [

                borough_gld,

                summary["avg_gld"]

            ]

        })

        fig = px.bar(

            comparison,

            x="Category",

            y="GLD",

            color="Category",

            text="GLD"

        )

        fig.update_traces(

            texttemplate="%{text:.1f}",

            textposition="outside"

        )

        fig.update_layout(

            height=450,

            showlegend=False,

            xaxis_title="",

            yaxis_title="GLD (%)",

            plot_bgcolor="white",

            paper_bgcolor="white"

        )

        return fig

