from shiny import ui
from shinywidgets import output_widget, render_plotly

import plotly.express as px


# =====================================================
# Interpretation guidance (Section 7.3 of the dissertation)
# =====================================================

CAVEAT_TEXT = (
    "These figures show statistical associations between borough averages. "
    "They do not show that one factor causes another, and they do not "
    "describe any individual child or family."
)


# =====================================================
# Styling
#
# The Overview was rebuilt after user acceptance testing, which found
# that unexplained acronyms and bare figures were the most common source
# of confusion. Each indicator is now presented as a single row carrying
# a plain-language title, the figure, and an explanation panel, so that
# no number appears without a statement of what it means.
#
# These rules belong in style.css alongside the other card styling; they
# are inlined here so the module renders correctly on its own.
# =====================================================

# Styling lives in style.css (see the Overview indicator rows section).


# =====================================================
# Building blocks
# =====================================================

def caveat_banner():
    return ui.div(CAVEAT_TEXT, class_="bley-caveat")


def band(icon, title, subtitle):
    """Section heading band."""
    return ui.div(
        ui.div(icon, class_="bley-band-icon"),
        ui.div(
            ui.p(title, class_="bley-band-title"),
            ui.p(subtitle, class_="bley-band-sub"),
        ),
        class_="bley-band",
    )


def indicator(icon, title, value, pill, *note_children):
    """One indicator: figure above, plain-language explanation below.

    No figure is displayed without an explanation, which is the change
    made in response to the acceptance testing reported in Section 5.3.
    """
    return ui.div(
        ui.div(
            ui.div(icon, class_="bley-ind-icon"),
            ui.div(title, class_="bley-ind-title"),
            ui.div(
                ui.div(value, class_="bley-ind-value"),
                ui.span(pill, class_="bley-ind-pill"),
                class_="bley-ind-figure",
            ),
            class_="bley-ind-card",
        ),
        ui.div(*note_children, class_="bley-ind-note"),
        class_="bley-ind",
    )


def ofsted_scale():
    """Visual key for the inspection scale, so the number has meaning."""
    items = [("4", "Outstanding", "chip-4"), ("3", "Good", "chip-3"),
             ("2", "Requires improvement", "chip-2"), ("1", "Inadequate", "chip-1")]
    return ui.div(
        *[ui.div(ui.div(n, class_=f"bley-chip {c}"), ui.span(label),
                 class_="bley-scale-item") for n, label, c in items],
        class_="bley-scale",
    )


# =====================================================
# Overview Page
# =====================================================

def overview_page(summary):

    df = summary["df"]

    gld_min, gld_max = df["gld"].min(), df["gld"].max()
    avg_childcare = df["childcare_per_100"].mean()
    avg_ofsted = df["ofsted"].mean()
    idaci = summary["avg_idaci"]

    return ui.nav_panel(

        "🏠 Overview",

        ui.div(
            ui.h1("BLEY"),
            ui.h2("A Decision Support System for Educational Attainment in London"),
            ui.p(
                "Exploring how socioeconomic, childcare and demographic "
                "indicators vary alongside early years outcomes across all "
                f"{len(df)} London boroughs."
            ),
            class_="dashboard-header",
        ),

        caveat_banner(),

        # -------------------------------------------------
        # Outcomes and provision
        # -------------------------------------------------

        band("📊", "Outcomes and childcare provision",
             "Key indicators of early years outcomes and provision across London."),

        indicator(
            "📈",
            "Average attainment at the end of early years (Good Level of Development)",
            f"{summary['avg_gld']:.1f}%",
            "Across London",
            ui.p("This is the percentage of children who reach the expected "
                 "standard for their age by the end of the reception year, "
                 "at around age five. Teachers assess each child on "
                 "communication, physical development, personal and social "
                 "development, literacy and mathematics."),
            ui.p(ui.tags.strong("Across London. "),
                 f"Boroughs range from {gld_min:.1f}% to {gld_max:.1f}%."),
        ),

        indicator(
            "🧸",
            "Number of registered early years childcare places",
            f"{avg_childcare:.1f}",
            "Places per 100 children under five",
            ui.p("This shows how many registered childcare places exist for "
                 "every 100 children aged under five living in the borough. A "
                 "higher number means more places are available locally "
                 "relative to the number of young children."),
        ),

        indicator(
            "⭐",
            "Childcare quality (Ofsted inspection)",
            f"{avg_ofsted:.2f}",
            "Average inspection rating",
            ui.p("This is the average inspection rating given by Ofsted, the "
                 "education regulator, across childcare providers in the "
                 "borough. Larger providers count for more, because they care "
                 "for more children. Ratings run from 1 to 4:"),
            ofsted_scale(),
            ui.p("Providers that have not yet been inspected are not included "
                 "in this average.", class_="bley-footnote"),
        ),

        # -------------------------------------------------
        # Local context
        # -------------------------------------------------

        band("📍", "Local context",
             "The wider circumstances of families living in each borough."),

        indicator(
            "🍽",
            "Free school meals eligibility",
            f"{summary['avg_fsm']:.1f}%",
            "Local indicator",
            ui.p("This is the share of pupils entitled to free school meals, "
                 "which families can claim when household income is low. It is "
                 "used here as a general signal of how many families in an "
                 "area are on a low income, rather than as a measure of any "
                 "individual family's circumstances."),
        ),

        indicator(
            "🌍",
            "Children living in lower-income households",
            f"{idaci * 100:.0f} in 100",
            "Income deprivation (IDACI)",
            ui.p("The Income Deprivation Affecting Children Index, or IDACI, "
                 "measures the proportion of children in an area living in "
                 "households with a low income. Across London this works out "
                 f"at roughly {idaci * 100:.0f} children in every 100, though "
                 "the figure varies considerably between boroughs."),
        ),

        indicator(
            "🧩",
            "Pupils with special educational needs",
            f"{summary['avg_sen']:.1f}%",
            "Local indicator",
            ui.p("This is the share of pupils identified as having special "
                 "educational needs, meaning they receive additional support "
                 "at school. A higher figure reflects how many children have "
                 "been identified locally. It does not indicate how good the "
                 "support available in that borough is, which this dashboard "
                 "does not measure."),
        ),

        ui.div(
            ui.div("i", class_="bley-closing-icon"),
            ui.div("Together these indicators describe early years outcomes, "
                   "how much childcare is available and how good it is, and "
                   "the wider circumstances of families in each borough. Use "
                   "the Borough Explorer to see any single borough in detail, "
                   "or What Fits Me Best to compare boroughs against the "
                   "things that matter most to you."),
            class_="bley-closing",
        ),

        ui.hr(),

        # -------------------------------------------------
        # Key Insights
        # -------------------------------------------------

        ui.h3("💡 Key Insights"),

        ui.layout_columns(

            ui.card(
                ui.card_header("🏆 Highest attainment"),
                ui.h4(summary["highest_gld"]["borough"]),
                ui.h2(f"{summary['highest_gld']['gld']:.1f}%"),
                class_="insight-card",
            ),

            ui.card(
                ui.card_header("📉 Lowest attainment"),
                ui.h4(summary["lowest_gld"]["borough"]),
                ui.h2(f"{summary['lowest_gld']['gld']:.1f}%"),
                class_="insight-card",
            ),

            ui.card(
                ui.card_header("↔ Difference between them"),
                ui.h4("Widest gap in London"),
                ui.h2(f"{gld_max - gld_min:.1f} pts"),
                class_="insight-card",
            ),

            ui.card(
                ui.card_header("🍽 Highest free school meals"),
                ui.h4(summary["highest_fsm"]["borough"]),
                ui.h2(f"{summary['highest_fsm']['fsm']:.1f}%"),
                class_="insight-card",
            ),

            col_widths=(3, 3, 3, 3),

        ),

        ui.hr(),

        # -------------------------------------------------
        # Chart
        # -------------------------------------------------

        ui.h3("📊 Every borough compared"),

        ui.p(
            "Each dot is one borough, ordered from highest to lowest. The "
            "dashed line marks the London average, so dots to the right of it "
            "are above average and dots to the left are below."
        ),

        output_widget("gld_chart"),

        ui.div(
            "The scale covers the range actually recorded rather than "
            "starting at zero, so position along the line carries the "
            "comparison. The differences are smaller than the spacing "
            f"suggests: all {len(df)} boroughs fall within "
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
                "gld": "Children reaching the expected standard (%)",
            },
        )

        fig.update_traces(
            marker=dict(size=11, color="#1F4E79"),
            hovertemplate="%{hovertext}<br>%{x:.1f}% reached the expected "
                          "standard<extra></extra>",
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
            xaxis_title="Children reaching the expected standard (%)",
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
