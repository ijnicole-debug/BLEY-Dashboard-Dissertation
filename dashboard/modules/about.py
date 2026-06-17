from shiny import ui


# =====================================================
# About Page
# =====================================================

def about_page():

    return ui.nav_panel(

        "ℹ️ About",

        ui.h2("About BLEY Educational Analytics Dashboard"),

        ui.hr(),

        ui.h3("Project Overview"),

        ui.p(
            """
            BLEY is an interactive educational analytics dashboard
            developed as part of an MSc Business Analytics dissertation.
            The dashboard explores the relationship between
            socioeconomic indicators and Good Level of Development
            (GLD) outcomes across London boroughs.
            """
        ),

        ui.hr(),

        ui.h3("Objectives"),

        ui.tags.ul(

            ui.tags.li(
                "Visualise educational attainment across London boroughs."
            ),

            ui.tags.li(
                "Explore relationships between deprivation indicators and GLD."
            ),

            ui.tags.li(
                "Present regression analysis results in an interactive format."
            ),

            ui.tags.li(
                "Provide a simple policy simulation tool."
            )

        ),

        ui.hr(),

        ui.h3("Data Sources"),

        ui.tags.ul(

            ui.tags.li(
                "Department for Education (DfE)"
            ),

            ui.tags.li(
                "Indices of Deprivation (IDACI)"
            ),

            ui.tags.li(
                "London borough-level socioeconomic indicators"
            )

        ),

        ui.hr(),

        ui.h3("Dashboard Features"),

        ui.tags.ul(

            ui.tags.li("Overview dashboard"),

            ui.tags.li("Borough Explorer"),

            ui.tags.li("Interactive Relationships"),

            ui.tags.li("Regression Results"),

            ui.tags.li("Policy Simulator")

        ),

        ui.hr(),

        ui.h3("Disclaimer"),

        ui.p(
            """
            This dashboard has been developed for academic purposes.
            The Simulator provides illustrative estimates based
            on individual regression models and should not be interpreted
            as official forecasts or policy recommendations.
            """
        )

    )