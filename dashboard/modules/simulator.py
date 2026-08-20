from shiny import ui, render, reactive

import pandas as pd
import statsmodels.api as sm
from scipy import stats


# =====================================================
# Model specification
# =====================================================

OUTCOME = "gld"

MODEL_PREDICTORS = [
    "childcare_per_100",
    "idaci",
    "fsm",
    "ethnic_diversity",
    "sen",
    "ofsted",
]

# Indicators exposed as sliders. The remaining model predictors are held
# at the Greater London average, which is stated on screen.
SLIDERS = [
    ("sim_childcare", "childcare_per_100", "Childcare places per 100 children", 0.1),
    ("sim_fsm", "fsm", "Free School Meals (%)", 0.1),
    ("sim_idaci", "idaci", "Income Deprivation (IDACI)", 0.005),
    ("sim_sen", "sen", "Special Educational Needs (%)", 0.1),
]

HELD_LABELS = {
    "ethnic_diversity": "Ethnic Diversity",
    "ofsted": "Ofsted Quality",
}

ALPHA = 0.05


# =====================================================
# Interpretation guidance 
# =====================================================

CAVEAT_TEXT = (
    "These figures show statistical associations between borough averages. "
    "They do not show that one factor causes another, and they do not "
    "describe any individual child or family."
)

SIMULATOR_CAVEAT = (
    "This is an arithmetic illustration of what the regression model "
    "implies, not a prediction. Changing an indicator in a real borough "
    "would not be expected to produce this result."
)

CAVEAT_CSS = """
.bley-caveat {
    background: #FFF4E5;
    border-left: 4px solid #C77700;
    padding: 10px 14px;
    margin: 8px 0 16px 0;
    font-size: 0.9rem;
    line-height: 1.45;
    color: #4A3000;
}
.bley-footnote {
    font-size: 0.8rem;
    color: #5A5A5A;
    margin-top: 6px;
    line-height: 1.5;
}
.bley-tier {
    font-size: 0.78rem;
    color: #5A5A5A;
    margin: -6px 0 10px 2px;
}
"""


def caveat_banner(text=CAVEAT_TEXT):
    return ui.div(text, class_="bley-caveat")


# =====================================================
# Model fitting and evidence tiers
# =====================================================

def evidence_tier(p_bivariate, p_multivariate):
    alone = p_bivariate < ALPHA
    adjusted = p_multivariate < ALPHA
    if alone and adjusted:
        return "● Strong evidence"
    if alone or adjusted:
        return "◐ Mixed evidence"
    return "○ Limited evidence"


def fit_simulator_model(df):
    data = df[[OUTCOME] + MODEL_PREDICTORS].dropna()
    model = sm.OLS(data[OUTCOME], sm.add_constant(data[MODEL_PREDICTORS])).fit()

    bounds, tiers = {}, {}
    for key in MODEL_PREDICTORS:
        bounds[key] = {
            "min": float(data[key].min()),
            "max": float(data[key].max()),
            "mean": float(data[key].mean()),
        }
        _, p_bi = stats.pearsonr(data[key], data[OUTCOME])
        tiers[key] = evidence_tier(p_bi, model.pvalues[key])

    return {
        "model": model,
        "bounds": bounds,
        "tiers": tiers,
        "gld_min": float(data[OUTCOME].min()),
        "gld_max": float(data[OUTCOME].max()),
        "gld_mean": float(data[OUTCOME].mean()),
        "gld_sd": float(data[OUTCOME].std(ddof=1)),
        "n": int(model.nobs),
    }


def _round_down(value, step):
    return round((value // step) * step, 3)


def _round_up(value, step):
    return round(-((-value) // step) * step, 3)


# =====================================================
# Policy Simulator Page
# =====================================================

def simulator_page(summary):

    fitted = fit_simulator_model(summary["df"])
    bounds = fitted["bounds"]
    tiers = fitted["tiers"]

    slider_blocks = []
    for input_id, key, label, step in SLIDERS:
        b = bounds[key]
        slider_blocks.append(
            ui.div(
                ui.input_slider(
                    input_id,
                    label,
                    min=_round_down(b["min"], step),
                    max=_round_up(b["max"], step),
                    value=round(b["mean"], 3),
                    step=step,
                ),
                ui.div(
                    f"{tiers[key]} · London average {b['mean']:.2f} · "
                    f"observed range {b['min']:.2f} to {b['max']:.2f}",
                    class_="bley-tier",
                ),
            )
        )

    held = ", ".join(
        f"{HELD_LABELS[k]} ({bounds[k]['mean']:.2f})"
        for k in MODEL_PREDICTORS if k in HELD_LABELS
    )

    return ui.nav_panel(

        "🤖 Policy Simulator",

        ui.tags.style(CAVEAT_CSS),

        ui.h2("Policy Simulator"),

        ui.p(
            "See what the regression model implies for boroughs with "
            "different combinations of these indicators. Sliders are limited "
            "to the range actually observed across London's 32 boroughs, "
            "because the model gives no meaningful values outside it."
        ),

        caveat_banner(),

        ui.hr(),

        ui.layout_columns(*slider_blocks[:2], col_widths=(6, 6)),
        ui.layout_columns(*slider_blocks[2:], col_widths=(6, 6)),

        ui.input_action_button(
            "sim_reset", "Reset to London average", class_="btn-secondary"
        ),

        ui.div(
            f"The remaining factors in the model are held at the Greater "
            f"London average: {held}. Evidence tiers are explained on the "
            f"Regression Results page; factors marked as limited evidence "
            f"showed no reliable association with GLD, so moving those "
            f"sliders reflects the model's arithmetic rather than an "
            f"established relationship.",
            class_="bley-footnote",
        ),

        ui.hr(),

        ui.card(
            ui.card_header("Modelled value"),
            ui.h2(ui.output_text("predicted_gld")),
            caveat_banner(SIMULATOR_CAVEAT),
        ),

        ui.br(),

        ui.card(
            ui.card_header("Interpretation"),
            ui.output_text("prediction_message"),
        ),
    )


# =====================================================
# Policy Simulator Server
# =====================================================

def simulator_server(input, output, session, summary):

    fitted = fit_simulator_model(summary["df"])
    model = fitted["model"]
    bounds = fitted["bounds"]

    gld_mean = fitted["gld_mean"]
    gld_min = fitted["gld_min"]
    gld_max = fitted["gld_max"]
    band = fitted["gld_sd"] / 2

    def _modelled():
        """Modelled GLD for the current slider settings."""
        row = {key: bounds[key]["mean"] for key in MODEL_PREDICTORS}
        for input_id, key, _, _ in SLIDERS:
            row[key] = float(getattr(input, input_id)())

        X = sm.add_constant(
            pd.DataFrame([row])[MODEL_PREDICTORS], has_constant="add"
        )
        return float(model.predict(X)[0])

    @reactive.effect
    @reactive.event(input.sim_reset)
    def _reset_sliders():
        for input_id, key, _, _ in SLIDERS:
            ui.update_slider(input_id, value=round(bounds[key]["mean"], 3))

    @render.text
    def predicted_gld():
        return f"{_modelled():.1f}%"

    @render.text
    def prediction_message():
        value = _modelled()
        difference = value - gld_mean

        if abs(difference) < band:
            position = (
                f"This is in line with the Greater London average of "
                f"{gld_mean:.1f}%. A difference of {abs(difference):.1f} "
                f"percentage points is small relative to the variation "
                f"between real boroughs."
            )
        elif difference > 0:
            position = (
                f"This is {difference:.1f} percentage points above the "
                f"Greater London average of {gld_mean:.1f}%."
            )
        else:
            position = (
                f"This is {abs(difference):.1f} percentage points below the "
                f"Greater London average of {gld_mean:.1f}%."
            )

        context = (
            f" Actual borough results range from {gld_min:.1f}% to "
            f"{gld_max:.1f}%."
        )

        if value < gld_min or value > gld_max:
            context += (
                " This combination produces a value outside the range any "
                "London borough actually records, so it should be read as an "
                "extrapolation beyond the data rather than a plausible "
                "outcome."
            )

        return position + context
