from shiny import ui, render
import pandas as pd


# =====================================================
# UI
# =====================================================

def recommendations_page(summary):

    return ui.nav_panel(

        "🏡 What Fits Me Best?",

        ui.h2("Personalised Borough Recommendations"),

        ui.p(
            """
            This tool helps families identify London boroughs
            that may best match their circumstances based on
            educational outcomes, deprivation levels and
            childcare accessibility.
            """
        ),

        ui.hr(),

        ui.h4("Tell us about your family"),

        ui.input_checkbox(
            "fsm_family",
            "Eligible for Free School Meals (FSM)"
        ),

        ui.input_checkbox(
            "sen_family",
            "Child has Special Educational Needs (SEN)"
        ),

        ui.input_checkbox(
            "low_income",
            "Low Income Household"
        ),

        ui.hr(),

        ui.h4("Recommended Boroughs"),

        ui.output_table("recommendations_table"),

        ui.hr(),

        ui.h4("Why these recommendations?"),

        ui.output_text_verbatim("recommendation_explanation")

    )


# =====================================================
# SERVER
# =====================================================

def recommendations_server(input, output, session, summary):

    df = summary["df"]

    @render.table
    def recommendations_table():

        recommendations = df.copy()

        # -----------------------------------------
        # Base suitability score
        # -----------------------------------------

        recommendations["score"] = (

            recommendations["gld"]
            + recommendations["childcare_per_100"]
            - recommendations["fsm"]
            - recommendations["sen"]
            - (recommendations["idaci"] * 100)

        )

        # -----------------------------------------
        # Personalisation
        # -----------------------------------------

        if input.fsm_family():

            recommendations["score"] -= recommendations["fsm"]

        if input.sen_family():

            recommendations["score"] -= recommendations["sen"]

        if input.low_income():

            recommendations["score"] -= (
                recommendations["idaci"] * 100
            )

        # -----------------------------------------
        # Ranking
        # -----------------------------------------

        recommendations = recommendations.sort_values(
            "score",
            ascending=False
        )

        # -----------------------------------------
        # Traffic light rating
        # -----------------------------------------

        recommendations["rating"] = "🟢 Strong Match"

        recommendations.loc[
            recommendations["score"] < 20,
            "rating"
        ] = "🟡 Moderate Match"

        recommendations.loc[
            recommendations["score"] < 0,
            "rating"
        ] = "🔴 Weak Match"

        recommendations["score"] = (
            recommendations["score"]
            .round(1)
        )

        return recommendations[
            ["borough", "score", "rating"]
        ].head(10)

    @render.text
    def recommendation_explanation():

        return """
How are recommendations generated?

The recommendation score combines:

• Good Level of Development (GLD)

• Childcare accessibility

• Free School Meal eligibility (FSM)

• Special Educational Needs prevalence (SEN)

• Income Deprivation Affecting Children Index (IDACI)

Boroughs with higher scores are considered
better matches according to the selected family profile.

The traffic-light rating provides a simple indication
of suitability:

🟢 Strong Match = Higher suitability

🟡 Moderate Match = Average suitability

🔴 Weak Match = Lower suitability

This tool is intended as an exploratory guide and
should not be interpreted as a definitive recommendation.
"""