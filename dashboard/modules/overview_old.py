from shiny import ui
from shinywidgets import output_widget, render_plotly

import plotly.express as px


# =====================================================
# =====================================================

CAVEAT_TEXT = (
    "These figures show statistical associations between borough averages. "
    "They do not show that one factor causes another, and they do not "
    "describe any individual child or family."
)

# .kpi-def, .bley-explainer and .bley-group belong in style.css
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
.kpi-def {
    font-size: 0.78rem;
    line-height: 1.4;
    color: rgba(255,255,255,.88) !important;
    margin: 6px 0 0 0;
    text-align: center;
}
.bley-explainer {
    background: #F5F9FD;
    border-left: 4px solid #2563EB;
    padding: 14px 18px;
    margin: 8px 0 18px 0;
    border-radius: 6px;
    line-height: 1.5;
}
.bley-explainer h4 {
    color: #1B365D;
    margin: 0 0 6px 0;
    font-size: 1.05rem;
    text-align: left;
}
.bley-group {
    font-size: 0.95rem;
    font-weight: 600;
    color: #1B365D;
    margin: 4px 0 8px 2px;
}
"""


def caveat_banner():
    return ui.div(CAVEAT_TEXT, class_="bley-caveat")


def kpi(header, value, definition):
    """A headline figure with a plain-language definition beneath it.

    Testing found that acronyms and bare numbers were the most common
    source of confusion, so no figure is shown without a definition.
    """
    return ui.card(
        ui.card_header(header),
        ui.h2(value),
        ui.p(definition, class_="kpi-def"),
        class_="kpi-card",
    )


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
                f"across all {len(df)} London boroughs."
            ),

            class_="dashboard-header"

        ),

        caveat_banner(),

        # -------------------------------------------------
        # What the outcome measure means
        # Added after testing: participants asked for an explanation of GLD.
        # -------------------------------------------------

        ui.div(
            ui.h4("What is a Good Level of Development?"),
            ui.p(
                "At the end of the reception year, teachers assess every child "
                "against the Early Years Foundation Stage Profile. A child who "
                "reaches the expected standard in communication and language, "
                "physical development, personal, social and emotional "
                "development, literacy and mathematics is recorded as having "
                "reached a Good Level of Development, or GLD. The figures "
                "below show the percentage of children in each borough who did "
                "so in the 2022/23 academic year."
            ),
            class_="bley-explainer",
        ),

        ui.hr(),

        # -------------------------------------------------
        # KPI Cards
        # Reduced from eight to six after testing, and grouped, in
        # response to feedback that the page carried too many figures.
        # -------------------------------------------------

        ui.div("Outcomes and childcare provision", class_="bley-group"),

        ui.layout_columns(

            kpi(
                "📈 Average GLD",
                f"{summary['avg_gld']:.1f}%",
                f"Across London. Boroughs range from {gld_min:.1f}% to "
                f"{gld_max:.1f}%.",
            ),

            kpi(
                "🧸 Childcare Places",
                f"{avg_childcare:.1f}",
                "Registered early years places for every 100 children aged "
                "under five.",
            ),

            kpi(
                "⭐ Ofsted Quality",
                f"{avg_ofsted:.2f}",
                "Average inspection grade, weighted by provider size. "
                "4 is Outstanding, 1 is Inadequate.",
            ),

            col_widths=(4, 4, 4),

        ),

        ui.br(),

        ui.div("Local context", class_="bley-group"),

        ui.layout_columns(

            kpi(
                "🎓 Free School Meals",
                f"{summary['avg_fsm']:.1f}%",
                "Share of pupils eligible for Free School Meals (FSM), used "
                "here as an indicator of concentrated disadvantage.",
            ),

            kpi(
                "🌍 Income Deprivation",
                f"{summary['avg_idaci']:.3f}",
                "Income Deprivation Affecting Children Index (IDACI): the "
                "share of children in income-deprived households, so "
                f"{summary['avg_idaci']:.3f} means about "
                f"{summary['avg_idaci'] * 100:.0f} in every 100.",
            ),

            kpi(
                "🧩 Special Educational Needs",
                f"{summary['avg_sen']:.1f}%",
                "Share of pupils identified as having Special Educational "
                "Needs (SEN) and requiring additional support.",
            ),

            col_widths=(4, 4, 4),

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
            "Each dot is one borough, ordered from highest to lowest. The "
            "dashed line marks the London average, so dots to the right of it "
            "are above average and dots to the left are below."
        ),

        output_widget("gld_chart"),

        ui.div(
            "The scale covers the observed range rather than starting at "
            "zero, so position along the axis carries the comparison. "
            "Differences between boroughs are smaller than the spacing "
            f"suggests: all {len(df)} fall within {gld_max - gld_min:.1f} "
            "percentage points of one another.",
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
                "gld": "Children reaching a Good Level of Development (%)",
            },
        )

        fig.update_traces(
            marker=dict(size=11, color="#1F4E79"),
            hovertemplate="%{hovertext}<br>%{x:.1f}% reached GLD<extra></extra>",
        )

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
            xaxis_title="Children reaching a Good Level of Development (%)",
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
