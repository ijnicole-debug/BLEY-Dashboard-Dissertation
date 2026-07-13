
from shiny import ui, render

# =====================================================
# Policy Simulator Page
# =====================================================

def simulator_page(summary):

    return ui.nav_panel(

        "🤖 Policy Simulator",

        ui.h2("Policy Simulator"),

        ui.p(
            """
            Explore how changes in key socioeconomic indicators
            may influence Good Level of Development (GLD)
            outcomes across London boroughs.
            """
        ),

        ui.hr(),

        ui.layout_columns(

            ui.input_slider(
                "sim_fsm",
                "Free School Meals (%)",
                min=0,
                max=50,
                value=summary["avg_fsm"],
                step=0.1
            ),

            ui.input_slider(
                "sim_sen",
                "Special Educational Needs (%)",
                min=0,
                max=30,
                value=summary["avg_sen"],
                step=0.1
            ),

            col_widths=(6,6)

        ),

        ui.layout_columns(

            ui.input_slider(
                "sim_idaci",
                "IDACI",
                min=0.0,
                max=1.0,
                value=summary["avg_idaci"],
                step=0.01
            ),

            ui.input_slider(
                "sim_childcare",
                "Childcare per 100",
                min=0,
                max=150,
                value=round(summary["df"]["childcare_per_100"].mean(),1),
                step=0.1
            ),

            col_widths=(6,6)

        ),

        ui.hr(),

        ui.card(

            ui.card_header("Estimated GLD (%)"),

            ui.h2(ui.output_text("predicted_gld"))

        ),

        ui.br(),

        ui.card(

            ui.card_header("Interpretation"),

            ui.output_text("prediction_message")

        )

    )


# =====================================================
# Policy Simulator Server
# =====================================================

def simulator_server(input, output, session, summary):

    avg_gld = summary["avg_gld"]
    avg_fsm = summary["avg_fsm"]
    avg_sen = summary["avg_sen"]
    avg_idaci = summary["avg_idaci"]
    avg_childcare = round(summary["df"]["childcare_per_100"].mean(),1)

    @render.text
    def predicted_gld():

        prediction = (

            avg_gld

            + (input.sim_fsm() - avg_fsm) * (-0.155)

            + (input.sim_sen() - avg_sen) * (-0.474)

            + (input.sim_idaci() - avg_idaci) * (-37.571)

            + (input.sim_childcare() - avg_childcare) * (0.125)

        )

        prediction = max(0, min(100, prediction))

        return f"{prediction:.1f}%"

    @render.text
    def prediction_message():

        prediction = (

            avg_gld

            + (input.sim_fsm() - avg_fsm) * (-0.155)

            + (input.sim_sen() - avg_sen) * (-0.474)

            + (input.sim_idaci() - avg_idaci) * (-37.571)

            + (input.sim_childcare() - avg_childcare) * (0.125)

        )

        if prediction >= avg_gld:
            return "Above the London average GLD."
        else:
            return "Below the London average GLD."

