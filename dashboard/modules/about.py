from shiny import ui

# The model specification is imported rather than restated, so this page
# can never disagree with the Regression Results page. The two import
# forms cover running as part of the modules package and running flat.
try:
    from modules.regression import fit_models, FULL_PREDICTORS
except ImportError:
    from regression import fit_models, FULL_PREDICTORS


# =====================================================
# Update these two lines when the underlying data is refreshed.
# =====================================================

DASHBOARD_VERSION = "1.0"
DATA_CURRENT_AS_AT = "August 2026"


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
.bley-meta {
    font-size: 0.8rem;
    color: #5A5A5A;
    margin-top: 24px;
}
"""


def caveat_banner(text=CAVEAT_TEXT):
    return ui.div(text, class_="bley-caveat")


# =====================================================
# Data sources
# =====================================================

SOURCES = [
    (
        "Good Level of Development (GLD)",
        "Department for Education, Early Years Foundation Stage Profile results",
        "2022/23",
        "https://explore-education-statistics.service.gov.uk/find-statistics/early-years-foundation-stage-profile-results/releases",
    ),
    (
        "Free School Meals eligibility",
        "Department for Education, School pupils and their characteristics",
        "2022/23",
        "https://explore-education-statistics.service.gov.uk/find-statistics/school-pupils-and-their-characteristics/2022-23",
    ),
    (
        "Special Educational Needs",
        "Department for Education, Special educational needs in England",
        "2022/23",
        "https://explore-education-statistics.service.gov.uk/find-statistics/special-educational-needs-in-england/2022-23",
    ),
    (
        "Income Deprivation Affecting Children Index (IDACI)",
        "Ministry of Housing, Communities and Local Government, English Indices of Deprivation",
        "2019",
        "https://www.gov.uk/government/statistics/english-indices-of-deprivation-2019",
    ),
    (
        "Childcare quality and registered places",
        "Ofsted, Childcare providers and inspections management information",
        "As at 31 December 2023",
        "https://www.gov.uk/government/statistical-data-sets/childcare-providers-and-inspections-management-information",
    ),
    (
        "Under-five population",
        "Office for National Statistics, Population estimates for England and Wales",
        "Mid-2022",
        "https://www.ons.gov.uk/peoplepopulationandcommunity/populationandmigration/populationestimates/datasets/estimatesofthepopulationforenglandandwales",
    ),
    (
        "Ethnic group composition",
        "Office for National Statistics, Census 2021 table TS021",
        "2021",
        "https://www.ons.gov.uk/datasets/TS021/editions/2021/versions/3",
    ),
    (
        "Average house prices (contextual only)",
        "HM Land Registry, UK House Price Index",
        "2025",
        "https://www.gov.uk/government/statistical-data-sets/uk-house-price-index-data-downloads-april-2026",
    ),
    (
        "Borough boundaries",
        "Greater London Authority, London Datastore and GLA ArcGIS services",
        "Current release",
        "https://data.london.gov.uk/dataset/london-boroughs-e55pw",
    ),
]


def _source_item(indicator, publisher, period, url):
    return ui.tags.li(
        ui.tags.strong(indicator),
        f" — {publisher}. Reference period: {period}. ",
        ui.tags.a("View source", href=url, target="_blank", rel="noopener"),
    )


# =====================================================
# About Page
# =====================================================

def about_page(summary):

    fitted = fit_models(summary["df"])
    model = fitted["full"]
    reduced = fitted["reduced"]
    results = fitted["results"]
    sensitivity = fitted["sensitivity"]
    n = fitted["n"]

    predictor_names = ", ".join(FULL_PREDICTORS.values())

    # Report the least robust significant association, if any.
    fragile = [
        s for s in sensitivity.values() if not s["robust"]
    ]
    fragile_note = ""
    if fragile:
        boroughs = sorted({s["borough"] for s in fragile})
        fragile_note = (
            "The statistically significant associations in this analysis "
            "depend heavily on a small number of boroughs. Removing "
            + " or ".join(boroughs)
            + ", which sits well outside the range of the other boroughs on "
            "childcare provision, leaves those associations no longer "
            "statistically significant. Findings should be read with that in "
            "mind."
        )

    return ui.nav_panel(

        "ℹ️ About",

        ui.tags.style(CAVEAT_CSS),

        ui.h2("About the BLEY Dashboard"),

        caveat_banner(),

        ui.hr(),

        # -------------------------------------------------
        # Overview
        # -------------------------------------------------

        ui.h3("Project Overview"),

        ui.p(
            "BLEY is an interactive analytics dashboard developed as part of "
            "an MSc Business Analytics dissertation. It brings together "
            "publicly available datasets on early years outcomes, "
            "deprivation, childcare provision and demography for the 32 "
            "London boroughs, and examines how these indicators vary "
            "alongside Good Level of Development (GLD) outcomes."
        ),

        ui.p(
            "The dashboard exists because these datasets are published "
            "separately, in different formats and at different levels of "
            "aggregation, which makes borough comparison difficult for "
            "anyone without the time or technical skills to combine them."
        ),

        ui.hr(),

        # -------------------------------------------------
        # Objectives
        # -------------------------------------------------

        ui.h3("Objectives"),

        ui.tags.ul(
            ui.tags.li(
                "Consolidate fragmented early years, socioeconomic, "
                "demographic and childcare data into a single borough-level "
                "dataset."
            ),
            ui.tags.li(
                "Construct comparable indicators from published sources."
            ),
            ui.tags.li(
                "Identify which indicators are associated with GLD outcomes "
                "across boroughs."
            ),
            ui.tags.li(
                "Present those associations through an interactive interface "
                "that non-technical users can operate."
            ),
            ui.tags.li(
                "Evaluate the resulting product through quality assurance and "
                "user acceptance testing."
            ),
        ),

        ui.hr(),

        # -------------------------------------------------
        # Data sources
        # -------------------------------------------------

        ui.h3("Data Sources"),

        ui.p(
            "Every figure in this dashboard is derived from the following "
            "published datasets. No data were collected directly, and no "
            "record relates to an identifiable individual."
        ),

        ui.tags.ul(*[_source_item(*source) for source in SOURCES]),

        ui.div(
            "Contains public sector information licensed under the Open "
            "Government Licence v3.0. Contains National Statistics data © "
            "Crown copyright and database right. Borough boundary data © "
            "Greater London Authority.",
            class_="bley-footnote",
        ),

        ui.hr(),

        # -------------------------------------------------
        # How the indicators were built
        # -------------------------------------------------

        ui.h3("How the Indicators Were Constructed"),

        ui.tags.ul(

            ui.tags.li(
                ui.tags.strong("Ofsted quality. "),
                "Inspection judgements are published on a four-point scale "
                "where 1 is Outstanding and 4 is Inadequate. A borough score "
                "is calculated as the average of the most recent judgement "
                "for each provider, weighted by that provider's registered "
                "places, and then rescaled so that 4 represents Outstanding. "
                "Providers with no inspection judgement are excluded from the "
                "quality measure but retained in the count of registered "
                "places, since the capacity exists whether or not the "
                "provider has been inspected."
            ),

            ui.tags.li(
                ui.tags.strong("Childcare availability. "),
                "Total registered places in a borough per 100 children aged "
                "under five."
            ),

            ui.tags.li(
                ui.tags.strong("Ethnic diversity. "),
                "Simpson's index of diversity, calculated across the 20 "
                "Census 2021 ethnic group categories. Values run from 0 to 1, "
                "with higher values indicating greater heterogeneity. The "
                "index is sensitive to the number of categories used, so "
                "values are comparable between boroughs but not with figures "
                "derived from a different classification."
            ),

            ui.tags.li(
                ui.tags.strong("IDACI. "),
                "The proportion of children in a borough living in "
                "income-deprived households, taken from the 2019 English "
                "Indices of Deprivation. The 2019 release is used in "
                "preference to later ones because it precedes the outcome "
                "year being analysed."
            ),

            ui.tags.li(
                ui.tags.strong("House prices. "),
                "Included as contextual information only. House prices are "
                "not part of the statistical model."
            ),

        ),

        ui.hr(),

        # -------------------------------------------------
        # Model specification
        # -------------------------------------------------

        ui.h3("The Statistical Model"),

        ui.p(
            f"The analysis uses ordinary least squares multiple regression "
            f"with GLD as the outcome and {len(FULL_PREDICTORS)} explanatory "
            f"variables: {predictor_names}. The dataset is cross-sectional, "
            f"covering a single academic year, with one observation per "
            f"borough (n = {n})."
        ),

        ui.tags.ul(
            ui.tags.li(
                f"Full model: R² = {model.rsquared:.3f}, adjusted R² = "
                f"{model.rsquared_adj:.3f}, F({int(model.df_model)}, "
                f"{int(model.df_resid)}) = {model.fvalue:.2f}, "
                f"p = {model.f_pvalue:.4f}."
            ),
            ui.tags.li(
                f"Reduced model (childcare availability and Free School Meals "
                f"only): R² = {reduced.rsquared:.3f}, adjusted R² = "
                f"{reduced.rsquared_adj:.3f}, p = {reduced.f_pvalue:.4f}. "
                f"Reported because {n} boroughs cannot reliably support "
                f"{len(FULL_PREDICTORS)} predictors."
            ),
            ui.tags.li(
                f"The full model accounts for {model.rsquared * 100:.1f}% of "
                f"the variation in GLD between boroughs, leaving "
                f"{(1 - model.rsquared) * 100:.1f}% unexplained."
            ),
        ),

        ui.p(
            "Full coefficients, confidence intervals, variance inflation "
            "factors and assumption checks are shown on the Regression "
            "Results page."
        ),

        ui.hr(),

        # -------------------------------------------------
        # Limitations
        # -------------------------------------------------

        ui.h3("Limitations"),

        ui.tags.ul(

            ui.tags.li(
                "The analysis identifies statistical associations. It does "
                "not establish that one factor causes another."
            ),

            ui.tags.li(
                "Every variable is a borough average. An association observed "
                "between borough averages may be stronger, weaker or opposite "
                "in direction to the relationship holding for individual "
                "children. Inferring the second from the first is known as "
                "the ecological fallacy."
            ),

            ui.tags.li(
                f"With {n} boroughs, the analysis can detect only reasonably "
                f"large associations. An indicator showing no reliable "
                f"association here may still matter."
            ),

            ui.tags.li(
                "Closely related measures, particularly IDACI and Free School "
                "Meals eligibility, overlap substantially and cannot be "
                "separated from one another at this sample size."
            ),

            *([ui.tags.li(fragile_note)] if fragile_note else []),

            ui.tags.li(
                "Ofsted childcare data are drawn from a release that "
                "partially post-dates the outcome year, and inspection "
                "coverage varies between boroughs."
            ),

            ui.tags.li(
                "The dashboard depends on the continued publication of these "
                "datasets in a comparable form."
            ),

        ),

        ui.hr(),

        # -------------------------------------------------
        # Features
        # -------------------------------------------------

        ui.h3("Dashboard Modules"),

        ui.tags.ul(
            ui.tags.li(
                ui.tags.strong("Overview. "),
                "Headline indicators and the distribution of GLD across "
                "boroughs."
            ),
            ui.tags.li(
                ui.tags.strong("Borough Explorer. "),
                "Interactive map and per-borough indicator profile."
            ),
            ui.tags.li(
                ui.tags.strong("Relationships. "),
                "Scatter plots and correlations between any two indicators."
            ),
            ui.tags.li(
                ui.tags.strong("Regression Results. "),
                "Model output in plain language, with full statistical detail "
                "and robustness checks."
            ),
            ui.tags.li(
                ui.tags.strong("Policy Simulator. "),
                "Modelled GLD values for different combinations of indicators."
            ),
            ui.tags.li(
                ui.tags.strong("What Fits Me Best. "),
                "Boroughs ranked against user-selected priorities."
            ),
            ui.tags.li(
                ui.tags.strong("About. "),
                "Sources, methods, model specification and limitations."
            ),
        ),

        ui.hr(),

        # -------------------------------------------------
        # Disclaimer
        # -------------------------------------------------

        ui.h3("Disclaimer"),

        ui.p(
            "This dashboard was developed for academic purposes and is not an "
            "official statistical publication. It does not represent the "
            "views of any of the organisations whose data it uses."
        ),

        caveat_banner(SIMULATOR_CAVEAT),

        ui.p(
            "Rankings and colour scales show a borough's position relative to "
            "other London boroughs. They are not judgements of performance, "
            "and many of the indicators shown reflect conditions outside a "
            "local authority's control."
        ),

        ui.div(
            f"BLEY Dashboard version {DASHBOARD_VERSION}. Data current as at "
            f"{DATA_CURRENT_AS_AT}. Figures on this page are calculated from "
            f"the loaded dataset each time the dashboard starts.",
            class_="bley-meta",
        ),

    )
