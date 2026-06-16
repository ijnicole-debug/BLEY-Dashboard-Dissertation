
from shiny import ui


def kpi_card(title, value):

    return ui.card(

        ui.card_header(title),

        ui.h2(value)

    )


def insight_card(title, borough, value):

    return ui.card(

        ui.card_header(title),

        ui.h4(borough),

        ui.p(value)

    )

