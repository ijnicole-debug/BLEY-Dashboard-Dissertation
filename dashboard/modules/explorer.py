
from shiny import ui, render
from shinywidgets import output_widget, render_plotly

import plotly.express as px


# =====================================================
# Explorer Page
# =====================================================

def explorer_page(summary):

    boroughs = sorted(summary["df"]["borough"].unique())

    return ui.nav_panel(

        "📊 Borough Explorer",

        ui.h2("Borough Explorer"),

        ui.p(
            """
            Explore educational attainment and deprivation
            indicators for individual London boroughs.
            """
        ),

        ui.input_select(

            "selected_borough",

            "Select Borough",

            choices=boroughs

        ),

        ui.hr(),

        ui.layout_columns(

            ui.card(

                ui.card_header("Borough Profile"),

                ui.output_table("borough_table")

            ),

            ui.card(

                ui.card_header("GLD Comparison"),

                output_widget("borough_chart")

            ),

            col_widths=(5,7)

        )

    )


# =====================================================
# Explorer Server
# =====================================================

def explorer_server(input, output, session, summary):

    df = summary["df"]

    @render.table
    def borough_table():

        borough = input.selected_borough()

        row = df[df["borough"] == borough].iloc[0]

        profile = {

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

        }

        return profile


    @render_plotly
    def borough_chart():

        borough = input.selected_borough()

        row = df[df["borough"] == borough].iloc[0]

        london_average = summary["avg_gld"]

        chart_df = {

            "Category": [

                borough,

                "London Average"

            ],

            "GLD": [

                row["gld"],

                london_average

            ]

        }

        fig = px.bar(

            chart_df,

            x="Category",

            y="GLD",

            color="Category",

            text="GLD"

        )

        fig.update_layout(

            height=450,

            showlegend=False,

            plot_bgcolor="white",

            paper_bgcolor="white",

            title=None

        )

        return fig

