from shiny import ui
from shinywidgets import output_widget, render_plotly

import plotly.express as px


# =====================================================
# Interpretation guidance (Section 7.3 of the dissertation)
# NOTE: duplicated in relationships.py, regression.py and simulator.py.
# Move all four into components.py.
# =====================================================

CAVEAT_TEXT = (
    "These figures show statistical associations between borough averages. "
    "They do not show that one factor causes another, and they do not "
    "describe any individual child or family."
)

CAVEAT_CSS = """
.bley-caveat {
    background: #FFF4E5;
    border-left: 4px solid #C77700;
    padding: 10px 14px;
    margin: 8px 0 16px 0;
    font-size: 0.9rem;
    line-height: 1.45;
    color: #4A3000;
}
.bley-footnote {
    font-size: 0.8rem;
    color: #5A5A5A;
    margin-top: 6px;
    line-height: 1.5;
}
"""


def caveat_banner():
    return ui.div(CAVEAT_TEXT, class_="bley-caveat")


# =====================================================
# Overview Page
# =====================================================

def overview_page(summary):

    df = summary["df"]

    gld_min = df["gld"].min()
    gld_max = df["gld"].max()
    avg_childcare = df["childcare_per_100"].mean()
    avg_ofsted = df["ofsted"].mean()

    return ui.nav_panel(

        "🏠 Overview",

        ui.tags.style(CAVEAT_CSS),

        # -------------------------------------------------
        # Header
        # -------------------------------------------------

        ui.div(

            ui.h1("BLEY"),

            ui.h2("A Decision Support System for Educational Attainment in London"),

            ui.p(
                "Exploring how socioeconomic, childcare and demographic "
                "indicators vary alongside Good Level of Development outcomes "
                "across London boroughs."
            ),

            class_="dashboard-header"

        ),

        caveat_banner(),

        ui.hr(),

        # -------------------------------------------------
        # KPI Cards
        # -------------------------------------------------

        ui.layout_columns(

            ui.card(
                ui.card_header("🏛 London Boroughs"),
                ui.h2(f"{len(df)}"),
                class_="kpi-card"
            ),

            ui.card(
                ui.card_header("📈 Average GLD (%)"),
                ui.h2(f"{summary['avg_gld']:.1f}"),
                class_="kpi-card"
            ),

            ui.card(
                ui.card_header("📊 GLD Range (%)"),
                ui.h2(f"{gld_min:.1f} – {gld_max:.1f}"),
                class_="kpi-card"
            ),

            ui.card(
                ui.card_header("🧸 Childcare Places per 100"),
                ui.h2(f"{avg_childcare:.1f}"),
                class_="kpi-card"
            ),

            col_widths=(3, 3, 3, 3)

        ),

        ui.br(),

        ui.layout_columns(

            ui.card(
                ui.card_header("🎓 Average FSM (%)"),
                ui.h2(f"{summary['avg_fsm']:.1f}"),
                class_="kpi-card"
            ),

            ui.card(
                ui.card_header("🧩 Average SEN (%)"),
                ui.h2(f"{summary['avg_sen']:.1f}"),
                class_="kpi-card"
            ),

            ui.card(
                ui.card_header("🌍 Average IDACI"),
                ui.h2(f"{summary['avg_idaci']:.3f}"),
                class_="kpi-card"
            ),

            ui.card(
                ui.card_header("⭐ Ofsted Quality (4 = Outstanding)"),
                ui.h2(f"{avg_ofsted:.2f}"),
                class_="kpi-card"
            ),

            col_widths=(3, 3, 3, 3)

        ),

        ui.div(
            "IDACI is the proportion of children in a borough living in "
            "income-deprived households, so a score of "
            f"{summary['avg_idaci']:.3f} means around "
            f"{summary['avg_idaci'] * 100:.1f}% of children on average. "
            "Ofsted quality is a places-weighted average of inspection "
            "judgements, rescaled so that 4 is Outstanding and 1 is "
            "Inadequate; providers without an inspection grade are excluded.",
            class_="bley-footnote",
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
                ui.h2(f"{summary['highest_gld']['gld']:.1f}%"),
                class_="insight-card"
            ),

            ui.card(
                ui.card_header("📉 Lowest GLD"),
                ui.h4(summary["lowest_gld"]["borough"]),
                ui.h2(f"{summary['lowest_gld']['gld']:.1f}%"),
                class_="insight-card"
            ),

            ui.card(
                ui.card_header("↔ Highest Minus Lowest"),
                ui.h4("Widest gap in London"),
                ui.h2(f"{gld_max - gld_min:.1f} pts"),
                class_="insight-card"
            ),

            ui.card(
                ui.card_header("🎓 Highest FSM"),
                ui.h4(summary["highest_fsm"]["borough"]),
                ui.h2(f"{summary['highest_fsm']['fsm']:.1f}%"),
                class_="insight-card"
            ),

            col_widths=(3, 3, 3, 3)

        ),

        ui.hr(),

        # -------------------------------------------------
        # GLD Chart
        # -------------------------------------------------

        ui.h3("📊 Good Level of Development by Borough"),

        ui.p(
            "Boroughs are ordered from highest to lowest. The dashed line "
            "marks the Greater London average."
        ),

        output_widget("gld_chart"),

        ui.div(
            "Values are shown on a scale covering the observed range rather "
            "than starting at zero, so position along the axis carries the "
            "comparison. Differences between boroughs are smaller than the "
            "spacing suggests: all 32 fall within "
            f"{gld_max - gld_min:.1f} percentage points of one another.",
            class_="bley-footnote",
        ),

    )


# =====================================================
# Overview Server
# =====================================================

def overview_server(input, output, session, summary):

    df = summary["df"]

    @render_plotly
    def gld_chart():

        ordered = df.sort_values("gld", ascending=True)
        mean_gld = df["gld"].mean()

        fig = px.scatter(
            ordered,
            x="gld",
            y="borough",
            hover_name="borough",
            labels={
                "borough": "London Borough",
                "gld": "Good Level of Development (%)",
            },
        )

        fig.update_traces(marker=dict(size=11, color="#1F4E79"))

        fig.add_vline(
            x=mean_gld,
            line_dash="dash",
            line_color="#C0392B",
            annotation_text=f"London average {mean_gld:.1f}%",
            annotation_position="top",
        )

        fig.update_layout(
            height=760,
            title=None,
            xaxis_title="Good Level of Development (%)",
            yaxis_title=None,
            plot_bgcolor="white",
            paper_bgcolor="white",
            margin=dict(l=10, r=30, t=40, b=40),
        )

        fig.update_xaxes(
            range=[df["gld"].min() - 2, df["gld"].max() + 2],
            gridcolor="#EDEDED",
        )

        fig.update_yaxes(gridcolor="#F5F5F5")

        return fig
