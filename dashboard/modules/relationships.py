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
    "ethnic_diversity": "Ethnic Diversity",
}

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
}
"""


def caveat_banner():
    """Fixed, non-dismissible interpretation guidance."""
    return ui.div(CAVEAT_TEXT, class_="bley-caveat")


# =====================================================
# Correlation strength bands - Evans (1996)
# Bands are continuous, so every coefficient falls in exactly one band.
# =====================================================

def strength_label(r):
    a = abs(r)
    if a < 0.20:
        return "Very weak"
    if a < 0.40:
        return "Weak"
    if a < 0.60:
        return "Moderate"
    if a < 0.80:
        return "Strong"
    return "Very strong"


def strength_display(r):
    if pd.isna(r):
        return "Not available"
    direction = "negative" if r < 0 else "positive"
    return f"{strength_label(r)} ({direction})"


# Set to False for uncluttered screenshots; borough names remain on hover.
SHOW_POINT_LABELS = True


# =====================================================
# Relationships Page
# =====================================================

def relationships_page(summary):

    return ui.nav_panel(

        "📈 Relationships",

        ui.tags.style(CAVEAT_CSS),

        ui.h2("Relationships Between Educational Factors"),

        ui.p(
            "Compare how any two indicators vary across London's 32 boroughs. "
            "Each point represents one borough, and the trend line summarises "
            "the pattern across boroughs as a whole."
        ),

        caveat_banner(),

        ui.layout_columns(

            ui.input_select(
                "x_variable",
                "Compare this factor",
                choices=VARIABLES,
                selected="fsm",
            ),

            ui.input_select(
                "y_variable",
                "Against this factor",
                choices=VARIABLES,
                selected="gld",
            ),

            col_widths=(6, 6),
        ),

        ui.hr(),

        # Repeated immediately above the chart, so the caveat is visible at the
        # point where a relationship is actually being read.
        caveat_banner(),

        output_widget("relationship_chart"),

        ui.hr(),

        ui.h3("Relationship Summary"),

        ui.output_table("relationship_summary"),

        ui.div(
            "Strength bands follow Evans (1996): below 0.20 very weak, "
            "0.20 to 0.39 weak, 0.40 to 0.59 moderate, 0.60 to 0.79 strong, "
            "0.80 and above very strong. Association does not imply causation.",
            class_="bley-footnote",
        ),

        ui.hr(),

        ui.h3("What does this mean?"),

        ui.output_text("relationship_interpretation"),
    )


# =====================================================
# Relationships Server
# =====================================================

def relationships_server(input, output, session, summary):

    df = summary["df"]

    def _corr(x, y):
        if x == y:
            return None
        return df[x].corr(df[y])

    @render_plotly
    def relationship_chart():

        x = input.x_variable()
        y = input.y_variable()

        fig = px.scatter(
            df,
            x=x,
            y=y,
            text="borough" if SHOW_POINT_LABELS else None,
            hover_name="borough",
            trendline="ols" if x != y else None,
            trendline_color_override="#C0392B",
            color=y,
            color_continuous_scale="Viridis",
            labels={x: VARIABLES[x], y: VARIABLES[y]},
        )

        fig.update_traces(
            textposition="top center",
            textfont=dict(size=9),
        )

        fig.update_layout(
            height=650,
            showlegend=False,
            coloraxis_showscale=False,   # colour bar duplicated the y axis
            plot_bgcolor="white",
            paper_bgcolor="white",
            margin=dict(t=40, r=20),
        )

        return fig

    @render.table
    def relationship_summary():

        x = input.x_variable()
        y = input.y_variable()
        corr = _corr(x, y)

        summary_df = pd.DataFrame({
            "Measure": [
                "Correlation",
                "Strength of association",
                "Average " + VARIABLES[x],
                "Average " + VARIABLES[y],
                "Number of Boroughs",
            ],
            "Value": [
                "Not applicable" if corr is None else round(corr, 2),
                "Not applicable" if corr is None else strength_display(corr),
                round(df[x].mean(), 2),
                round(df[y].mean(), 2),
                len(df),
            ],
        })

        return summary_df

    @render.text
    def relationship_interpretation():

        x = input.x_variable()
        y = input.y_variable()
        corr = _corr(x, y)

        if corr is None:
            return (
                "Please select two different indicators to see how they "
                "vary together across boroughs."
            )

        band = strength_label(corr)
        higher_lower = "lower" if corr < 0 else "higher"

        closing = (
            "\n\nThis pattern describes boroughs as a whole. It does not "
            "describe individual children or families, and it does not show "
            "that one factor causes the other."
        )

        if band == "Very weak":
            return (
                f"There is little consistent association between "
                f"{VARIABLES[x]} and {VARIABLES[y]} across London's boroughs.\n\n"
                f"Boroughs with higher {VARIABLES[x]} are no more likely to "
                f"record higher or lower {VARIABLES[y]} than any other borough."
                + closing
            )

        openers = {
            "Weak": "a weak",
            "Moderate": "a moderate",
            "Strong": "a strong",
            "Very strong": "a very strong",
        }

        return (
            f"There is {openers[band]} {'negative' if corr < 0 else 'positive'} "
            f"association between {VARIABLES[x]} and {VARIABLES[y]} "
            f"across London's boroughs.\n\n"
            f"Boroughs with higher {VARIABLES[x]} tend to record "
            f"{higher_lower} {VARIABLES[y]}, though individual boroughs "
            f"depart from this pattern."
            + closing
        )
