
from shiny import ui
from shinywidgets import output_widget, render_plotly

import plotly.express as px


# =====================================================
# Overview Page
# =====================================================

def overview_page(summary):

    return ui.nav_panel(

        "🏠 Overview",

        # -------------------------------------------------
        # Header
        # -------------------------------------------------

        ui.h1("BLEY"),

        ui.h2("A Decision Support System for Educational Attainment in London"),

        ui.p(
            """
            Supporting evidence-based policy decisions by exploring
            the relationship between socioeconomic deprivation
            indicators and Good Level of Development (GLD)
            outcomes across London boroughs.
            """
        ),

        ui.hr(),

        # -------------------------------------------------
        # KPI Cards
        # -------------------------------------------------

        ui.layout_columns(

            ui.card(
                ui.card_header("🏛 London Boroughs"),
                ui.h2(f"{summary['total_boroughs']}")
            ),

            ui.card(
                ui.card_header("📈 Average GLD (%)"),
                ui.h2(f"{summary['avg_gld']:.1f}")
            ),

            ui.card(
                ui.card_header("🎓 Average FSM (%)"),
                ui.h2(f"{summary['avg_fsm']:.1f}")
            ),

            ui.card(
                ui.card_header("🧩 Average SEN (%)"),
                ui.h2(f"{summary['avg_sen']:.1f}")
            ),

            col_widths=(3, 3, 3, 3)

        ),

        ui.br(),

        ui.layout_columns(

            ui.card(
                ui.card_header("🌍 Average IDACI Score"),
                ui.h2(f"{summary['avg_idaci']:.1f}")
            ),

            ui.card(
                ui.card_header("📋 Dataset Size"),
                ui.h2(f"{len(summary['df'])} Boroughs")
            ),

            col_widths=(6, 6)

        ),

        ui.hr(),

        # -------------------------------------------------
        # Key Insights
        # -------------------------------------------------

        ui.h3("💡 Key Insights"),

        ui.layout_columns(

            ui.card(

                ui.card_header("🏆 Highest GLD"),

                ui.h4(summary["highest_gld"]["borough"]),

                ui.h2(f"{summary['highest_gld']['gld']:.1f}%")

            ),

            ui.card(

                ui.card_header("📉 Lowest GLD"),

                ui.h4(summary["lowest_gld"]["borough"]),

                ui.h2(f"{summary['lowest_gld']['gld']:.1f}%")

            ),

            ui.card(

                ui.card_header("🎓 Highest FSM"),

                ui.h4(summary["highest_fsm"]["borough"]),

                ui.h2(f"{summary['highest_fsm']['fsm']:.1f}%")

            ),

            col_widths=(4, 4, 4)

        ),

        ui.hr(),

        # -------------------------------------------------
        # GLD Chart
        # -------------------------------------------------

        ui.h3("📊 Good Level of Development by Borough"),

        output_widget("gld_chart"),

        ui.hr(),

        # -------------------------------------------------
        # FSM Chart
        # -------------------------------------------------

        ui.h3("📈 Relationship Between FSM and GLD"),

        output_widget("fsm_chart")

    )


# =====================================================
# Overview Server
# =====================================================

def overview_server(input, output, session, summary):

    df = summary["df"]

    # -------------------------------------------------
    # GLD by Borough
    # -------------------------------------------------

    @render_plotly
    def gld_chart():

        fig = px.bar(

            df.sort_values("gld", ascending=False),

            x="borough",

            y="gld",

            color="gld",

            color_continuous_scale="Blues",

            labels={

                "borough": "London Borough",

                "gld": "Good Level of Development (%)"

            }

        )

        fig.update_layout(

            height=500,

            title=None,

            xaxis_title="London Borough",

            yaxis_title="GLD (%)",

            xaxis_tickangle=-45,

            plot_bgcolor="white",

            paper_bgcolor="white"

        )

        return fig

    # -------------------------------------------------
    # FSM vs GLD
    # -------------------------------------------------

    @render_plotly
    def fsm_chart():

        fig = px.scatter(

            df,

            x="fsm",

            y="gld",

            text="borough",

            trendline="ols",

            color="gld",

            color_continuous_scale="Blues"

        )

        fig.update_traces(

            textposition="top center",

            marker=dict(size=12)

        )

        fig.update_layout(

            height=500,

            title=None,

            xaxis_title="Free School Meals (%)",

            yaxis_title="Good Level of Development (%)",

            plot_bgcolor="white",

            paper_bgcolor="white"

        )

        return fig

