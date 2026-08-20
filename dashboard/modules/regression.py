from shiny import ui, render

import numpy as np
import pandas as pd
import statsmodels.api as sm
from statsmodels.stats.diagnostic import het_breuschpagan
from statsmodels.stats.outliers_influence import variance_inflation_factor
from scipy import stats


# =====================================================
# Model specification
#
# =====================================================

OUTCOME = "gld"
OUTCOME_LABEL = "Good Level of Development (GLD)"

FULL_PREDICTORS = {
    "childcare_per_100": "Childcare Availability",
    "idaci": "Income Deprivation (IDACI)",
    "fsm": "Free School Meals (FSM)",
    "ethnic_diversity": "Ethnic Diversity",
    "sen": "Special Educational Needs (SEN)",
    "ofsted": "Ofsted Quality (4 = Outstanding)",
}

REDUCED_PREDICTORS = ["childcare_per_100", "fsm"]

ALPHA = 0.05


# =====================================================
# Interpretation guidance 
# =====================================================

CAVEAT_TEXT = (
    "These figures show statistical associations between borough averages. "
    "They do not show that one factor causes another, and they do not "
    "describe any individual child or family."
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
.bley-section h4 {
    margin-top: 18px;
    margin-bottom: 6px;
}
"""


def caveat_banner():
    """Fixed, non-dismissible interpretation guidance."""
    return ui.div(CAVEAT_TEXT, class_="bley-caveat")


# =====================================================
# Evidence tiers
#
# Each factor is assessed twice: on its own, through a bivariate
# correlation, and alongside the other factors, through the multiple
# regression. 
# =====================================================

def evidence_tier(p_bivariate, p_multivariate):
    alone = p_bivariate < ALPHA
    adjusted = p_multivariate < ALPHA

    if alone and adjusted:
        return "● Strong evidence"
    if alone or adjusted:
        return "◐ Mixed evidence"
    return "○ Limited evidence"


EVIDENCE_NOTE = (
    "Each factor is assessed twice. 'On its own' is the correlation between "
    "that factor and GLD across boroughs. 'Alongside other factors' is its "
    "contribution in the multiple regression model, holding the other five "
    "constant. Strong evidence means the association holds in both; mixed "
    "evidence means it holds in one but not the other, usually because two "
    "factors overlap and compete to explain the same variation; limited "
    "evidence means neither reached statistical significance at p < 0.05."
)

POWER_NOTE = (
    "This analysis covers 32 boroughs. A sample of this size can detect only "
    "reasonably large differences, so a factor showing limited evidence here "
    "may still matter. The dataset is too small to establish it either way."
)


# =====================================================
# Model fitting
# =====================================================

def _bivariate(df, key):
    r, p = stats.pearsonr(df[key], df[OUTCOME])
    return r, p


def _leave_one_out(df, key):
    """Borough whose removal changes the bivariate correlation most."""
    base_r, _ = _bivariate(df, key)
    worst_name, worst_r, worst_p, worst_shift = None, base_r, 1.0, 0.0

    for i in df.index:
        subset = df.drop(index=i)
        r, p = stats.pearsonr(subset[key], subset[OUTCOME])
        shift = abs(base_r - r)
        if shift > worst_shift:
            worst_name = df.loc[i, "borough"]
            worst_r, worst_p, worst_shift = r, p, shift

    return {
        "borough": worst_name,
        "base_r": base_r,
        "r_without": worst_r,
        "p_without": worst_p,
        "robust": worst_p < ALPHA,
    }


def fit_models(df):
    cols = [OUTCOME] + list(FULL_PREDICTORS)
    data = df[cols + ["borough"]].dropna().reset_index(drop=True)

    y = data[OUTCOME]
    X_full = sm.add_constant(data[list(FULL_PREDICTORS)])
    full = sm.OLS(y, X_full).fit()

    X_red = sm.add_constant(data[REDUCED_PREDICTORS])
    reduced = sm.OLS(y, X_red).fit()

    sd_y = y.std(ddof=1)
    rows = []

    for key, label in FULL_PREDICTORS.items():
        r, p_bi = _bivariate(data, key)
        coef = full.params[key]
        ci_low, ci_high = full.conf_int().loc[key]

        rows.append({
            "key": key,
            "label": label,
            "r": r,
            "p_bi": p_bi,
            "coef": coef,
            "se": full.bse[key],
            "p_mv": full.pvalues[key],
            "ci_low": ci_low,
            "ci_high": ci_high,
            "beta": coef * (data[key].std(ddof=1) / sd_y) if sd_y else np.nan,
        })

    results = pd.DataFrame(rows)
    results["vif"] = [
        variance_inflation_factor(X_full.values, i)
        for i in range(1, len(FULL_PREDICTORS) + 1)
    ]
    results["evidence"] = results.apply(
        lambda row: evidence_tier(row["p_bi"], row["p_mv"]), axis=1
    )

    # Sensitivity check on whichever factors are significant on their own.
    sensitivity = {
        row["key"]: _leave_one_out(data, row["key"])
        for _, row in results.iterrows()
        if row["p_bi"] < ALPHA
    }

    diagnostics = {
        "shapiro_p": stats.shapiro(full.resid).pvalue,
        "bp_p": het_breuschpagan(full.resid, full.model.exog)[1],
        "max_vif": results["vif"].max(),
    }

    return {
        "data": data,
        "full": full,
        "reduced": reduced,
        "results": results,
        "sensitivity": sensitivity,
        "diagnostics": diagnostics,
        "n": int(full.nobs),
    }


def plain_finding(row):
    """Plain-language description combining both tests."""

    if row["p_bi"] >= ALPHA and row["p_mv"] >= ALPHA:
        return (
            f"This analysis found limited evidence that {row['label'].lower()} "
            f"was associated with differences in GLD."
        )

    direction = "higher" if row["r"] > 0 else "lower"

    if row["p_bi"] < ALPHA and row["p_mv"] < ALPHA:
        return (
            f"Boroughs with greater {row['label'].lower()} generally recorded "
            f"{direction} GLD, and this held once the other factors were "
            f"taken into account."
        )

    if row["p_bi"] < ALPHA:
        return (
            f"Boroughs with greater {row['label'].lower()} generally recorded "
            f"{direction} GLD, but this did not hold once the other factors "
            f"were taken into account."
        )

    return (
        f"{row['label']} contributed to the model alongside the other "
        f"factors, but showed no clear association with GLD on its own."
    )


def _p(p):
    return "<0.001" if p < 0.001 else f"{p:.3f}"


# =====================================================
# REGRESSION RESULTS PAGE
# =====================================================

def regression_page(summary):

    return ui.nav_panel(

        "📉 Regression Results",

        ui.tags.style(CAVEAT_CSS),

        ui.h2("Which Factors Are Associated with Early Years Outcomes?"),

        ui.p(
            "This page examines which factors are associated with Good Level "
            "of Development (GLD) outcomes across London's 32 boroughs. Each "
            "factor is tested twice: on its own, and alongside the others in "
            "a multiple regression model."
        ),

        caveat_banner(),

        ui.hr(),

        ui.h3("What the Analysis Found"),

        ui.output_table("regression_table"),

        ui.div(EVIDENCE_NOTE, class_="bley-footnote"),
        ui.div(POWER_NOTE, class_="bley-footnote"),

        ui.br(),

        ui.accordion(
            ui.accordion_panel(
                "Show statistical detail",
                ui.output_text("model_fit"),
                ui.br(),
                ui.output_table("regression_detail"),
                ui.div(
                    "Coefficients are unstandardised: each shows the change in "
                    "GLD percentage points associated with a one-unit "
                    "difference in that factor, holding the others constant. "
                    "Standardised coefficients allow factors measured on "
                    "different scales to be compared. VIF is the variance "
                    "inflation factor; values above 5 indicate that a "
                    "predictor overlaps substantially with the others.",
                    class_="bley-footnote",
                ),
                ui.br(),
                ui.output_text("diagnostics_text"),
            ),
            ui.accordion_panel(
                "How robust are these findings?",
                ui.output_ui("sensitivity_panel"),
            ),
            open=False,
        ),

        ui.hr(),

        ui.h3("Main Findings"),

        ui.output_ui("main_findings"),

        ui.hr(),

        ui.h3("What Does This Mean for Decision-Makers?"),

        ui.output_ui("regression_interpretation"),
    )


# =====================================================
# REGRESSION SERVER
# =====================================================

def regression_server(input, output, session, summary):

    fitted = fit_models(summary["df"])

    results = fitted["results"]
    full = fitted["full"]
    reduced = fitted["reduced"]
    sensitivity = fitted["sensitivity"]
    diag = fitted["diagnostics"]
    n = fitted["n"]

    both = results[(results["p_bi"] < ALPHA) & (results["p_mv"] < ALPHA)]
    mixed = results[
        ((results["p_bi"] < ALPHA) | (results["p_mv"] < ALPHA))
        & ~((results["p_bi"] < ALPHA) & (results["p_mv"] < ALPHA))
    ]
    limited = results[(results["p_bi"] >= ALPHA) & (results["p_mv"] >= ALPHA)]

    @render.table
    def regression_table():
        return pd.DataFrame({
            "Factor": results["label"],
            "On its own": results.apply(
                lambda r: f"r = {r['r']:+.2f} (p = {_p(r['p_bi'])})", axis=1
            ),
            "Alongside other factors": results["p_mv"].apply(
                lambda p: f"p = {_p(p)}"
            ),
            "What this means": results.apply(plain_finding, axis=1),
            "Evidence": results["evidence"],
        })

    @render.text
    def model_fit():
        red_names = ", ".join(FULL_PREDICTORS[k] for k in REDUCED_PREDICTORS)
        return (
            f"Full model (pre-specified, {len(FULL_PREDICTORS)} factors), "
            f"n = {n}\n"
            f"  R² = {full.rsquared:.3f}   "
            f"Adjusted R² = {full.rsquared_adj:.3f}\n"
            f"  F({int(full.df_model)}, {int(full.df_resid)}) = "
            f"{full.fvalue:.2f}, p = {full.f_pvalue:.4f}\n\n"
            f"Reduced model (sensitivity analysis: {red_names})\n"
            f"  R² = {reduced.rsquared:.3f}   "
            f"Adjusted R² = {reduced.rsquared_adj:.3f}\n"
            f"  F({int(reduced.df_model)}, {int(reduced.df_resid)}) = "
            f"{reduced.fvalue:.2f}, p = {reduced.f_pvalue:.4f}\n\n"
            f"With {n} boroughs, {len(FULL_PREDICTORS)} predictors leave "
            f"roughly {n / len(FULL_PREDICTORS):.0f} observations each, which "
            f"is below the level normally considered adequate. The reduced "
            f"model is reported for comparison."
        )

    @render.table
    def regression_detail():
        return pd.DataFrame({
            "Factor": results["label"],
            "Correlation": results["r"].round(3),
            "Coefficient": results["coef"].round(3),
            "Std. error": results["se"].round(3),
            "95% CI": results.apply(
                lambda r: f"{r['ci_low']:.2f} to {r['ci_high']:.2f}", axis=1
            ),
            "Standardised": results["beta"].round(3),
            "p-value": results["p_mv"].apply(_p),
            "VIF": results["vif"].round(2),
        })

    @render.text
    def diagnostics_text():
        return (
            "Assumption checks on the full model\n"
            f"  Normality of residuals (Shapiro-Wilk): "
            f"p = {diag['shapiro_p']:.3f}\n"
            f"  Constant variance (Breusch-Pagan): p = {diag['bp_p']:.3f}\n"
            f"  Highest variance inflation factor: {diag['max_vif']:.2f}\n"
            "  Values above 0.05 for the first two indicate the assumption is "
            "not violated."
        )

    @render.ui
    def sensitivity_panel():
        if not sensitivity:
            return ui.p(
                "No factor reached statistical significance on its own, so no "
                "sensitivity check applies."
            )

        items = []
        for key, s in sensitivity.items():
            label = FULL_PREDICTORS[key]
            verdict = (
                "The association remains statistically significant without "
                "that borough."
                if s["robust"] else
                "The association is no longer statistically significant "
                "without that borough, so this finding rests heavily on a "
                "single case and should be treated with caution."
            )
            items.append(ui.tags.li(
                f"{label}: correlation with GLD is {s['base_r']:+.2f} across "
                f"all {n} boroughs. Removing {s['borough']}, the most "
                f"influential single case, changes it to {s['r_without']:+.2f} "
                f"(p = {_p(s['p_without'])}). {verdict}"
            ))

        return ui.div(
            ui.p(
                "Each significant association was re-tested with every borough "
                "removed in turn. The borough with the largest effect on each "
                "result is reported below."
            ),
            ui.tags.ul(*items),
        )

    @render.ui
    def main_findings():
        cards = []

        if not both.empty:
            top = both.reindex(
                both["beta"].abs().sort_values(ascending=False).index
            ).iloc[0]
            cards.append(ui.card(
                ui.h4(f"📈 {top['label']}"),
                ui.p(
                    f"{top['label']} showed the clearest association with GLD "
                    f"in this analysis, holding both on its own and alongside "
                    f"the other factors. Boroughs with greater "
                    f"{top['label'].lower()} generally recorded higher GLD "
                    f"outcomes. This is an association between borough "
                    f"averages, not evidence that increasing it would raise "
                    f"outcomes."
                ),
            ))

        if not mixed.empty:
            labels = " and ".join(mixed["label"].tolist())
            cards.append(ui.card(
                ui.h4("📉 " + labels),
                ui.p(
                    f"{labels} each showed a significant association with GLD "
                    f"when examined on their own, but neither retained that "
                    f"association once all factors were modelled together. "
                    f"These measures overlap closely, so they compete to "
                    f"explain the same variation between boroughs. The "
                    f"pattern is real; which specific measure captures it "
                    f"cannot be separated with 32 boroughs."
                ),
            ))

        if not limited.empty:
            labels = ", ".join(limited["label"].tolist())
            cards.append(ui.card(
                ui.h4("❓ Factors with Limited Evidence"),
                ui.p(
                    f"This analysis found no reliable evidence that {labels} "
                    f"were associated with differences in GLD across these "
                    f"boroughs. {POWER_NOTE}"
                ),
            ))

        spaced = []
        for card in cards:
            spaced.extend([card, ui.br()])
        return ui.div(*spaced)

    @render.ui
    def regression_interpretation():

        strongest = None
        if not both.empty:
            strongest = both.reindex(
                both["beta"].abs().sort_values(ascending=False).index
            ).iloc[0]["label"]

        mixed_labels = " and ".join(mixed["label"].tolist())
        limited_labels = limited["label"].tolist()

        families = [ui.h4("For parents and families")]
        if strongest:
            families.append(ui.p(
                f"Among the factors examined, {strongest.lower()} showed the "
                f"clearest association with early years outcomes across "
                f"boroughs."
            ))
        if mixed_labels:
            families.append(ui.p(
                f"Boroughs with higher levels of socioeconomic disadvantage, "
                f"measured through {mixed_labels.lower()}, also tended to "
                f"record lower GLD."
            ))
        families.append(ui.p(
            "These are borough-wide patterns. They describe areas as a whole "
            "and cannot indicate how any individual child is likely to do, so "
            "several factors are worth weighing together rather than any "
            "single indicator."
        ))

        policy = [ui.h4("For local authorities and policy makers")]
        policy.append(ui.p(
            f"The model accounts for {full.rsquared * 100:.1f}% of the "
            f"variation in GLD between boroughs, leaving "
            f"{(1 - full.rsquared) * 100:.1f}% unexplained. Overall model "
            f"significance is p = {full.f_pvalue:.3f}."
        ))
        policy.append(ui.p(
            "These associations indicate where borough conditions and "
            "outcomes diverge from the wider pattern, which is a prompt for "
            "local enquiry rather than an explanation. They should not be "
            "read as evidence that changing any single indicator would "
            "produce a corresponding change in outcomes."
        ))

        limits = []
        if limited_labels:
            limits = [
                ui.h4("Factors with limited evidence"),
                ui.p("No reliable association with GLD was identified for:"),
                ui.tags.ul(*[ui.tags.li(x) for x in limited_labels]),
                ui.p(POWER_NOTE),
            ]

        caveats = [
            ui.h4("Important limitations"),
            ui.tags.ul(
                ui.tags.li(
                    "Regression identifies statistical associations. It does "
                    "not establish that one factor causes another."
                ),
                ui.tags.li(
                    "All variables are borough averages. Associations between "
                    "borough averages may be stronger, weaker or opposite in "
                    "direction to the relationships holding for individual "
                    "children."
                ),
                ui.tags.li(
                    f"With {n} boroughs, the analysis has limited power to "
                    f"detect smaller associations, and closely related "
                    f"measures cannot be separated from one another."
                ),
                ui.tags.li(
                    "Early years outcomes are shaped by many factors, "
                    "including factors not included in this model."
                ),
            ),
        ]

        return ui.div(*families, *policy, *limits, *caveats,
                      class_="bley-section")
