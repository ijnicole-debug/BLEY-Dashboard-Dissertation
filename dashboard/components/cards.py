from shiny import ui


def kpi_card(title, value, class_="kpi-card"):
    """A single headline metric. Styled by .kpi-card in style.css."""

    return ui.card(
        ui.card_header(title),
        ui.h2(value),
        class_=class_,
    )


def insight_card(title, subtitle, value, class_="insight-card"):
    """A named borough with its value. Styled by .insight-card."""

    return ui.card(
        ui.card_header(title),
        ui.h4(subtitle),
        ui.h2(value),
        class_=class_,
    )
