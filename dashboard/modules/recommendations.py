from shiny import ui, render
import pandas as pd


# =====================================================
# UI
# =====================================================

def recommendations_page(summary):

    min_price = int(summary["df"]["average_house_price"].min())
    max_price = int(summary["df"]["average_house_price"].max())
    median_price = int(summary["df"]["average_house_price"].median())

    return ui.nav_panel(

        "🏡 What Fits Me Best?",

        ui.h2("Personalised Borough Recommendation"),

        ui.p(
            """
            This decision support tool recommends London boroughs
            that best match a family's circumstances using an
            evidence-based multi-criteria recommendation model.
            """
        ),

        ui.hr(),

        ui.h4("Family Profile"),

        ui.layout_columns(

            ui.input_checkbox(
                "fsm_family",
                "Eligible for Free School Meals (FSM)"
            ),

            ui.input_checkbox(
                "sen_family",
                "Child has Special Educational Needs (SEN)"
            ),

            ui.input_slider(

                "housing_budget",

                "Maximum Housing Budget (£)",

                min=min_price,

                max=max_price,

                value=median_price,

                step=25000,

                pre="£",

                sep=","

            ),

            col_widths=(3, 3, 6)

        ),

        ui.hr(),

        ui.h4("Recommended Boroughs"),

        ui.output_table("recommendations_table"),

        ui.hr(),

        ui.h4("How are recommendations generated?"),

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

        # =====================================================
        # NORMALISE VARIABLES
        # =====================================================

        recommendations["gld_norm"] = (
            (recommendations["gld"] - recommendations["gld"].min())
            /
            (recommendations["gld"].max() - recommendations["gld"].min())
        )

        recommendations["childcare_norm"] = (
            (recommendations["childcare_per_100"] - recommendations["childcare_per_100"].min())
            /
            (recommendations["childcare_per_100"].max() - recommendations["childcare_per_100"].min())
        )

        recommendations["fsm_norm"] = 1 - (
            (recommendations["fsm"] - recommendations["fsm"].min())
            /
            (recommendations["fsm"].max() - recommendations["fsm"].min())
        )

        recommendations["idaci_norm"] = 1 - (
            (recommendations["idaci"] - recommendations["idaci"].min())
            /
            (recommendations["idaci"].max() - recommendations["idaci"].min())
        )

        recommendations["house_norm"] = 1 - (
            (recommendations["average_house_price"] - recommendations["average_house_price"].min())
            /
            (recommendations["average_house_price"].max() - recommendations["average_house_price"].min())
        )

        recommendations["sen_norm"] = 1 - (
            (recommendations["sen"] - recommendations["sen"].min())
            /
            (recommendations["sen"].max() - recommendations["sen"].min())
        )

        # =====================================================
        # DEFAULT EVIDENCE-BASED WEIGHTS
        # =====================================================

        weights = {

            "gld": 0.35,

            "childcare": 0.25,

            "idaci": 0.20,

            "fsm": 0.15,

            "house": 0.05,

            "sen": 0.00

        }

        # =====================================================
        # PERSONALISE WEIGHTS
        # =====================================================

        if input.fsm_family():

            weights["gld"] += 0.05
            weights["idaci"] += 0.05
            weights["fsm"] += 0.05

        if input.sen_family():

            weights["childcare"] += 0.05
            weights["sen"] += 0.15
            weights["gld"] -= 0.05

        # =====================================================
        # NORMALISE WEIGHTS
        # =====================================================

        total_weight = sum(weights.values())

        for key in weights:

            weights[key] /= total_weight

        # =====================================================
        # HOUSING BUDGET PENALTY
        # =====================================================

        budget = input.housing_budget()

        recommendations["budget_penalty"] = 1.0

        mask = recommendations["average_house_price"] > budget

        recommendations.loc[
            mask,
            "budget_penalty"
        ] = (
            budget /
            recommendations.loc[
                mask,
                "average_house_price"
            ]
        )

        # =====================================================
        # SUITABILITY SCORE
        # =====================================================

        recommendations["score"] = (

            recommendations["gld_norm"] * weights["gld"] +

            recommendations["childcare_norm"] * weights["childcare"] +

            recommendations["idaci_norm"] * weights["idaci"] +

            recommendations["fsm_norm"] * weights["fsm"] +

            recommendations["house_norm"] * weights["house"] +

            recommendations["sen_norm"] * weights["sen"]

        )

        recommendations["score"] = (

            recommendations["score"]

            * recommendations["budget_penalty"]

            * 100

        ).round(2)
        
        # =====================================================
        # RANK BOROUGHS
        # =====================================================

        recommendations = recommendations.sort_values(
            "score",
            ascending=False
        ).reset_index(drop=True)

        recommendations["Rank"] = (
            recommendations.index + 1
        )

        # =====================================================
        # TRAFFIC LIGHT CLASSIFICATION
        # =====================================================

        recommendations["Recommendation"] = "🟢 Excellent Match"

        recommendations.loc[
            recommendations["score"] < 80,
            "Recommendation"
        ] = "🟡 Good Match"

        recommendations.loc[
            recommendations["score"] < 65,
            "Recommendation"
        ] = "🟠 Fair Match"

        recommendations.loc[
            recommendations["score"] < 50,
            "Recommendation"
        ] = "🔴 Less Suitable"

        # =====================================================
        # FORMAT HOUSE PRICES
        # =====================================================

        recommendations["Average House Price"] = (

            "£"

            + recommendations["average_house_price"]
            .round(0)
            .astype(int)
            .map("{:,}".format)

        )

        # =====================================================
        # RETURN TABLE
        # =====================================================

        return (

            recommendations[
                [
                    "Rank",
                    "borough",
                    "score",
                    "Average House Price",
                    "Recommendation"
                ]
            ]

            .rename(
                columns={
                    "borough": "Borough",
                    "score": "Suitability Score"
                }
            )

            .head(10)

        )

    # =====================================================
    # EXPLANATION
    # =====================================================

    @render.text
    def recommendation_explanation():

        profile = []

        if input.fsm_family():

            profile.append(
                "Eligible for Free School Meals (FSM)"
            )

        if input.sen_family():

            profile.append(
                "Child has Special Educational Needs (SEN)"
            )

        if len(profile) == 0:

            profile_text = (
                "No additional family characteristics selected."
            )

        else:

            profile_text = ", ".join(profile)

        budget = (
            f"£{input.housing_budget():,}"
        )

        return f"""
The recommendation engine uses an Evidence-Based Multi-Criteria Recommendation Model.

Methodology

1. Every variable is normalised to a common 0–1 scale using Min–Max Normalisation.

2. Evidence-based weights are informed by the regression analysis undertaken in this dissertation.

3. The recommendation score combines:

• Good Level of Development (GLD)
• Childcare availability
• Income Deprivation Affecting Children Index (IDACI)
• Free School Meals (FSM)
• Average house price

Your selected family profile

• {profile_text}

Maximum housing budget

• {budget}

Boroughs with average house prices above your selected housing budget are not removed. Instead, they receive a proportional affordability penalty, allowing educational performance and affordability to be considered simultaneously.

Higher suitability scores indicate boroughs that better match the selected family profile.
""" 