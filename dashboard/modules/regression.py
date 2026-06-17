from shiny import ui, render
import pandas as pd


# =====================================================
# Regression Results Page
# =====================================================

def regression_page(summary):

    return ui.nav_panel(

        "📉 Regression Results",

        ui.h2("Regression Analysis Results"),

        ui.p(
            """
            Individual linear regression results examining the
            relationship between socioeconomic indicators and
            Good Level of Development (GLD) outcomes across
            London boroughs.
            """
        ),

        ui.hr(),

        ui.h3("Regression Summary"),

        ui.output_table("regression_table"),

        ui.hr(),

        ui.h3("Key Findings"),

        ui.tags.ul(

            ui.tags.li(
                "Childcare per 100 has the strongest positive relationship with GLD (R² = 0.593, p < 0.001)."
            ),

            ui.tags.li(
                "IDACI has a statistically significant negative relationship with GLD (Coefficient = -37.571, p = 0.002)."
            ),

            ui.tags.li(
                "FSM is significantly associated with lower GLD outcomes (Coefficient = -0.155, p = 0.024)."
            ),

            ui.tags.li(
                "SEN, Ofsted and Ethnic Diversity are not statistically significant at the 5% level."
            )

        )

    )


# =====================================================
# Regression Server
# =====================================================

def regression_server(input, output, session, summary):

    @render.table
    def regression_table():

        regression_df = pd.DataFrame({

            "Variable": [

                "Free School Meals",

                "Special Educational Needs",

                "IDACI",

                "Ofsted",

                "Childcare per 100",

                "Ethnic Diversity"

            ],

            "Coefficient": [

                -0.155,

                -0.474,

                -37.571,

                -1.710,

                0.125,

                -38.768

            ],

            "P-value": [

                0.024,

                0.077,

                0.002,

                0.825,

                0.000,

                0.165

            ],

            "R²": [

                0.154,

                0.098,

                0.280,

                0.002,

                0.593,

                0.061

            ],

            "Significant (5%)": [

                "Yes",

                "No",

                "Yes",

                "No",

                "Yes",

                "No"

            ]

        })

        return regression_df