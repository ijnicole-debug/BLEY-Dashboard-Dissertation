from shiny import ui, render, reactive

import pandas as pd


# =====================================================
# Interpretation guidance 
# =====================================================

CAVEAT_TEXT = (
    "These figures show statistical associations between borough averages. "
    "They do not show that one factor causes another, and they do not "
    "describe any individual child or family."
)

RANKING_CAVEAT = (
    "Boroughs are ranked against the priorities you have selected. The "
    "ranking reflects currently published indicators, not any forecast of a "
    "child's outcomes, and it is not advice about where to live."
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


def caveat_banner(text=CAVEAT_TEXT):
    return ui.div(text, class_="bley-caveat")


# =====================================================
# Criteria
#
# Each criterion states the column it uses, the direction the user is
# assumed to prefer when they give it weight, and the units shown in the
# results table. 
# =====================================================

CRITERIA = {
    "gld": {
        "input": "w_gld",
        "label": "Early years outcomes (GLD)",
        "prefer": "high",
        "direction_text": "higher GLD scores more",
        "decimals": 1,
        "suffix": "%",
    },
    "childcare_per_100": {
        "input": "w_childcare",
        "label": "Childcare availability",
        "prefer": "high",
        "direction_text": "more places per 100 children scores more",
        "decimals": 1,
        "suffix": "",
    },
    "ofsted": {
        "input": "w_ofsted",
        "label": "Childcare quality (Ofsted)",
        "prefer": "high",
        "direction_text": "higher inspection quality scores more",
        "decimals": 2,
        "suffix": "",
    },
    "idaci": {
        "input": "w_idaci",
        "label": "Lower area deprivation (IDACI)",
        "prefer": "low",
        "direction_text": "lower deprivation scores more",
        "decimals": 3,
        "suffix": "",
    },
    "average_house_price": {
        "input": "w_price",
        "label": "Lower house prices",
        "prefer": "low",
        "direction_text": "lower average price scores more",
        "decimals": 0,
        "suffix": "",
    },
}

DEFAULT_WEIGHT = 3
MAX_WEIGHT = 5


# =====================================================
# UI
# =====================================================

def recommendations_page(summary):

    df = summary["df"]

    min_price = int(df["average_house_price"].min())
    max_price = int(df["average_house_price"].max())

    weight_sliders = [
        ui.div(
            ui.input_slider(
                meta["input"],
                meta["label"],
                min=0,
                max=MAX_WEIGHT,
                value=DEFAULT_WEIGHT,
                step=1,
            ),
            ui.div(
                f"0 = ignore this, {MAX_WEIGHT} = most important. "
                f"When weighted, {meta['direction_text']}.",
                class_="bley-footnote",
            ),
        )
        for meta in CRITERIA.values()
    ]

    first_row = weight_sliders[:3]
    second_row = weight_sliders[3:]

    slider_rows = [
        ui.layout_columns(*first_row, col_widths=[4] * len(first_row))
    ]
    if second_row:
        slider_rows.append(
            ui.layout_columns(*second_row, col_widths=[4] * len(second_row))
        )

    return ui.nav_panel(

        "🏡 What Fits Me Best?",

        ui.tags.style(CAVEAT_CSS),

        ui.h2("Compare Boroughs Against Your Priorities"),

        ui.p(
            "Set how much each factor matters to you and the boroughs will be "
            "ranked accordingly. The weights are yours to choose: there is no "
            "correct set, and this tool does not recommend one."
        ),

        caveat_banner(),

        ui.hr(),

        ui.h4("What matters to you?"),

        *slider_rows,

        ui.input_action_button(
            "reset_weights", "Reset all priorities", class_="btn-secondary"
        ),

        ui.hr(),

        ui.h4("Affordability filter"),

        ui.input_slider(
            "housing_budget",
            "Maximum average house price",
            min=min_price,
            max=max_price,
            value=max_price,
            step=25000,
            pre="£",
            sep=",",
        ),

        ui.input_checkbox(
            "hide_unaffordable",
            "Hide boroughs above this price",
            value=False,
        ),

        ui.div(
            "Affordability is kept separate from the ranking rather than "
            "folded into the score, so an expensive borough is never quietly "
            "downgraded on grounds unrelated to your priorities. Prices are "
            "borough averages across all property types and sizes.",
            class_="bley-footnote",
        ),

        ui.hr(),

        ui.h4("Boroughs Ranked by Your Priorities"),

        caveat_banner(RANKING_CAVEAT),

        ui.input_radio_buttons(
            "result_count",
            "Show",
            {"5": "Top 5", "10": "Top 10", "all": "All 32 boroughs"},
            selected="5",
            inline=True,
        ),

        ui.output_table("recommendations_table"),

        ui.div(
            "The top five are shown by default. Select 'All 32 boroughs' to "
            "find any borough, including your own. The match score is a "
            "relative position within Greater London, not a rating of "
            "quality. Because scores are rescaled across the range observed "
            "in London, boroughs at opposite ends of the list can differ by "
            "far less than the scores suggest: GLD, for example, varies by "
            "under 11 percentage points across the whole capital.",
            class_="bley-footnote",
        ),

        ui.hr(),

        ui.h4("How is the ranking calculated?"),

        ui.output_ui("recommendation_explanation"),
    )


# =====================================================
# SERVER
# =====================================================

def recommendations_server(input, output, session, summary):

    df = summary["df"]

    def _weights():
        return {
            column: float(getattr(input, meta["input"])())
            for column, meta in CRITERIA.items()
        }

    def _scored():
        """Rank boroughs against the user's stated priorities."""

        data = df.copy()
        weights = _weights()
        total = sum(weights.values())

        if total == 0:
            data["score"] = float("nan")
        else:
            score = 0
            for column, meta in CRITERIA.items():
                low, high = data[column].min(), data[column].max()
                spread = high - low

                if spread == 0:
                    normalised = pd.Series(0.5, index=data.index)
                else:
                    normalised = (data[column] - low) / spread
                    if meta["prefer"] == "low":
                        normalised = 1 - normalised

                score = score + normalised * (weights[column] / total)

            data["score"] = (score * 100).round(1)

        data = data.sort_values("score", ascending=False).reset_index(drop=True)
        data["Rank"] = data.index + 1
        return data

    @reactive.effect
    @reactive.event(input.reset_weights)
    def _reset():
        for meta in CRITERIA.values():
            ui.update_slider(meta["input"], value=DEFAULT_WEIGHT)

    @render.table
    def recommendations_table():

        data = _scored()
        weights = _weights()

        if sum(weights.values()) == 0:
            return pd.DataFrame({
                "Borough": ["Set at least one priority above to rank boroughs."]
            })

        budget = input.housing_budget()
        if input.hide_unaffordable():
            data = data[data["average_house_price"] <= budget]
            if data.empty:
                return pd.DataFrame({
                    "Borough": ["No borough has an average price at or below "
                                f"£{budget:,}."]
                })

        table = pd.DataFrame({
            "Rank": data["Rank"],
            "Borough": data["borough"],
            "Match score": data["score"],
        })

        # Show the underlying values behind the score, for every criterion
        # the user has actually weighted.
        for column, meta in CRITERIA.items():
            if weights[column] == 0:
                continue
            decimals = meta["decimals"]
            if column == "average_house_price":
                table[meta["label"]] = data[column].astype(int).map("£{:,}".format)
            else:
                table[meta["label"]] = (
                    data[column].round(decimals).astype(str) + meta["suffix"]
                )

        table["Within budget"] = [
            "Yes" if price <= budget else "No"
            for price in data["average_house_price"]
        ]

        choice = input.result_count()
        if choice != "all":
            table = table.head(int(choice))

        return table

    @render.ui
    def recommendation_explanation():

        weights = _weights()
        total = sum(weights.values())

        if total == 0:
            weighting = ui.p(
                "No priorities are currently set, so no ranking is produced."
            )
        else:
            items = [
                ui.tags.li(
                    f"{meta['label']}: {weights[column] / total * 100:.0f}% of "
                    f"the score ({meta['direction_text']})"
                )
                for column, meta in CRITERIA.items()
                if weights[column] > 0
            ]
            weighting = ui.div(
                ui.p("Your current priorities translate into these shares:"),
                ui.tags.ul(*items),
            )

        return ui.div(

            ui.h4("Method"),
            ui.tags.ol(
                ui.tags.li(
                    "Each indicator is rescaled to a 0 to 1 range using "
                    "min-max normalisation across the 32 boroughs, so that "
                    "indicators measured in different units can be combined."
                ),
                ui.tags.li(
                    "Indicators where you would prefer a lower value are "
                    "reversed, so that a lower figure produces a higher score. "
                    "This is stated beneath each slider rather than applied "
                    "silently."
                ),
                ui.tags.li(
                    "Each rescaled indicator is multiplied by the share of "
                    "the total weight you assigned to it, and the results are "
                    "added together to give a match score out of 100."
                ),
            ),

            weighting,

            ui.h4("What this ranking is not"),
            ui.tags.ul(
                ui.tags.li(
                    "The weights are your choices, not recommendations. They "
                    "are not derived from the regression analysis, and no "
                    "combination of weights is more correct than another."
                ),
                ui.tags.li(
                    "Every indicator is a borough average. A child does not "
                    "take on a borough's average outcome by living there, and "
                    "differences within a borough are typically larger than "
                    "differences between boroughs."
                ),
                ui.tags.li(
                    "A high score means a borough matches the priorities you "
                    "set. It does not mean the borough performs well, and "
                    "many of these indicators reflect conditions outside a "
                    "local authority's control."
                ),
                ui.tags.li(
                    "The dashboard holds no measure of provision for children "
                    "with special educational needs. SEN prevalence is not "
                    "included as a criterion, because a lower recorded rate "
                    "may reflect under-identification rather than better "
                    "support, and prevalence says nothing about the quality "
                    "of provision. Families needing SEN support should "
                    "contact the local authority's SEND information service "
                    "directly."
                ),
            ),
        )
