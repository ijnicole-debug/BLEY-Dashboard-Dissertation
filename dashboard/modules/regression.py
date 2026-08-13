from shiny import ui, render
import pandas as pd


# =====================================================
# REGRESSION RESULTS PAGE
# =====================================================

def regression_page(summary):

    return ui.nav_panel(

        "📉 Regression Results",

        ui.h2("What Influences Early Years Educational Outcomes?"),

        ui.p(
            """
            This page explains which factors are associated with
            Good Level of Development (GLD) outcomes across London's
            32 boroughs.

            The analysis helps identify patterns in the data.
            It does not prove that one factor directly causes
            changes in educational outcomes.
            """
        ),

        ui.hr(),

        ui.h3("What the Analysis Found"),

        ui.output_table("regression_table"),

        ui.hr(),

        ui.h3("Main Findings"),

        ui.card(

            ui.h4("📈 Childcare Availability"),

            ui.p(
                """
                Childcare availability showed the strongest positive
                relationship with GLD in this analysis.

                In simple terms, boroughs with greater childcare
                availability generally had higher GLD outcomes.
                """
            )

        ),

        ui.br(),

        ui.card(

            ui.h4("📉 Income Deprivation and Free School Meals"),

            ui.p(
                """
                Income deprivation (IDACI) and Free School Meal
                eligibility showed negative relationships with GLD.

                In simple terms, boroughs with higher levels of
                socioeconomic disadvantage generally had lower
                GLD outcomes.
                """
            )

        ),

        ui.br(),

        ui.card(

            ui.h4("❓ Factors with Limited Evidence"),

            ui.p(
                """
                The analysis did not find statistically reliable
                evidence that SEN prevalence, average Ofsted rating
                or ethnic diversity explained differences in GLD
                across the boroughs in this dataset.

                This does not mean these factors are unimportant.
                It means that this particular analysis did not find
                sufficient evidence of a reliable relationship.
                """
            )

        ),

        ui.hr(),

        ui.h3("What Does This Mean for Decision-Makers?"),

        ui.output_text_verbatim("regression_interpretation")

    )


# =====================================================
# REGRESSION SERVER
# =====================================================

def regression_server(input, output, session, summary):

    @render.table
    def regression_table():

        regression_df = pd.DataFrame({

            "Factor": [

                "Childcare Availability",

                "Income Deprivation (IDACI)",

                "Free School Meals (FSM)",

                "Ethnic Diversity",

                "Special Educational Needs (SEN)",

                "Average Ofsted Rating"

            ],

            "What the analysis found": [

                "Boroughs with greater childcare availability generally achieved higher GLD outcomes.",

                "Higher levels of income deprivation were associated with lower GLD outcomes.",

                "Higher levels of FSM eligibility were associated with lower GLD outcomes.",

                "The analysis found limited evidence of a reliable relationship with GLD.",

                "The analysis found limited evidence that SEN prevalence explained differences in GLD.",

                "The analysis found limited evidence that average Ofsted ratings explained differences in GLD."

            ],

            "Evidence": [

                "🟢 Strong Evidence",

                "🟢 Strong Evidence",

                "🟢 Strong Evidence",

                "⚪ Limited Evidence",

                "⚪ Limited Evidence",

                "⚪ Limited Evidence"

            ]

        })

        return regression_df


    @render.text
    def regression_interpretation():

        return """
FOR PARENTS AND FAMILIES

The results suggest that childcare availability is an important
factor to consider when comparing London boroughs.

Boroughs with greater childcare availability generally achieved
higher early years educational outcomes.

The analysis also found that boroughs with higher levels of
socioeconomic disadvantage generally recorded lower GLD outcomes.

This means families may wish to consider several factors together,
including educational outcomes, childcare availability and the
socioeconomic conditions of an area.


FOR LOCAL AUTHORITIES AND POLICYMAKERS

The strongest positive relationship identified in this analysis
was between childcare availability and GLD.

The analysis also identified negative relationships between GLD
and both income deprivation and Free School Meal eligibility.

These findings suggest that policies supporting childcare
availability and disadvantaged families may be relevant when
considering strategies to improve early years educational outcomes.

However, the findings should not be interpreted as evidence that
increasing childcare availability alone will automatically cause
GLD outcomes to improve.


FACTORS WITH LIMITED EVIDENCE

The analysis did not identify statistically reliable relationships
between GLD and:

• Special Educational Needs (SEN)

• Average Ofsted Rating

• Ethnic Diversity

This does not mean that these factors are unimportant.

It means that the available data did not provide sufficient
statistical evidence to conclude that these factors were reliably
associated with differences in GLD across the boroughs.


IMPORTANT LIMITATION

Regression analysis identifies statistical relationships between
variables.

It does not prove that one factor directly causes another.

Educational outcomes are influenced by many factors, including
factors that were not included in this analysis.
"""