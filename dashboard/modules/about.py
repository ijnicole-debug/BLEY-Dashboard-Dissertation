
from shiny import ui


def about_page():

    return ui.nav_panel(

        "ℹ About",

        ui.h2("About BLEY"),

        ui.p(
            """
            BLEY is an interactive Decision Support System
            developed as part of an MSc Data Analytics dissertation.
            """
        )

    )

