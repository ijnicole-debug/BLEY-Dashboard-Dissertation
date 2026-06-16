
from shiny import App, ui
from shinywidgets import output_widget, render_plotly

import pandas as pd
import plotly.express as px

# =====================================================
# Load data
# =====================================================

df = pd.read_csv("data/master_dataset.csv")

# =====================================================
# Summary statistics
# =====================================================

total_boroughs = df["borough"].nunique()

avg_gld = round(df["gld"].mean(), 1)
avg_fsm = round(df["fsm"].mean(), 1)
avg_sen = round(df["sen"].mean(), 1)
avg_idaci = round(df["idaci"].mean(), 1)

highest_gld = df.loc[df["gld"].idxmax()]
lowest_gld = df.loc[df["gld"].idxmin()]
highest_fsm = df.loc[df["fsm"].idxmax()]

# =====================================================
# User Interface
# =====================================================

app_ui = ui.page_fluid(

    # -------------------------------------------------

    ui.h1("BLEY"),

    ui.h2("An Interactive Dashboard for Educational Attainment in London"),

    ui.p(
        """
        Dashboard for exploring
        the relationship between socioeconomic deprivation indicators
        and Good Level of Development (GLD) outcomes across London boroughs.
        """
    ),

    ui.hr(),

    # -------------------------------------------------
    # KPI CARDS
    # -------------------------------------------------

    ui.layout_columns(

        ui.card(
            ui.card_header("🏛 London Boroughs"),
            ui.h2(f"{total_boroughs}")
        ),

        ui.card(
            ui.card_header("📈 Average GLD (%)"),
            ui.h2(f"{avg_gld:.1f}")
        ),

        ui.card(
            ui.card_header("🎓 Average FSM (%)"),
            ui.h2(f"{avg_fsm:.1f}")
        ),

        ui.card(
            ui.card_header("🧩 Average SEN (%)"),
            ui.h2(f"{avg_sen:.1f}")
        ),

        col_widths=(3, 3, 3, 3)

    ),

    ui.br(),

    ui.layout_columns(

        ui.card(
            ui.card_header("🌍 Average IDACI Score"),
            ui.h2(f"{avg_idaci:.1f}")
        ),

        ui.card(
            ui.card_header("📋 Dataset Size"),
            ui.h2(f"{len(df)} Boroughs")
        ),

        col_widths=(6, 6)

    ),

    ui.hr(),

    # -------------------------------------------------
    # KEY INSIGHTS
    # -------------------------------------------------

    ui.h3("💡 Key Insights"),

    ui.layout_columns(

        ui.card(

            ui.card_header("🏆 Highest GLD"),

            ui.h4(highest_gld["borough"]),

            ui.p(f"{highest_gld['gld']:.1f}%")

        ),

        ui.card(

            ui.card_header("📉 Lowest GLD"),

            ui.h4(lowest_gld["borough"]),

            ui.p(f"{lowest_gld['gld']:.1f}%")

        ),

        ui.card(

            ui.card_header("🎓 Highest FSM"),

            ui.h4(highest_fsm["borough"]),

            ui.p(f"{highest_fsm['fsm']:.1f}%")

        ),

        col_widths=(4, 4, 4)

    ),

    ui.hr(),

    # -------------------------------------------------
    # GLD CHART
    # -------------------------------------------------

    ui.h3("📊 Good Level of Development by Borough"),

    output_widget("gld_chart"),

    ui.hr(),

    # -------------------------------------------------
    # FSM CHART
    # -------------------------------------------------

    ui.h3("📈 Relationship Between FSM and GLD"),

    output_widget("fsm_chart")

)

# =====================================================
# Server
# =====================================================

def server(input, output, session):

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

            xaxis_tickangle=-45,

            plot_bgcolor="white",

            paper_bgcolor="white"

        )

        return fig

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

        fig.update_traces(textposition="top center")

        fig.update_layout(

            height=500,

            title=None,

            plot_bgcolor="white",

            paper_bgcolor="white"

        )

        return fig


# =====================================================

app = App(app_ui, server)

