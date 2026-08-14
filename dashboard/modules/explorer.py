from shiny import ui, render
from shinywidgets import output_widget, render_plotly

from pathlib import Path
import json

import pandas as pd
import plotly.express as px


# =====================================================
# GeoJSON loading
#
# Anchored to this file rather than the working directory, so the module
# behaves the same locally and on ShinyApps.io.
# =====================================================

_HERE = Path(__file__).resolve().parent
_CANDIDATES = [
    _HERE / "data" / "london_boroughs_wgs84.geojson",
    _HERE.parent / "data" / "london_boroughs_wgs84.geojson",
    Path("data/london_boroughs_wgs84.geojson"),
]

GEOJSON_PATH = next((p for p in _CANDIDATES if p.exists()), None)
if GEOJSON_PATH is None:
    raise FileNotFoundError(
        "london_boroughs_wgs84.geojson not found. Looked in: "
        + ", ".join(str(p) for p in _CANDIDATES)
    )

with open(GEOJSON_PATH, "r") as f:
    london_geojson = json.load(f)

FEATURE_KEY = "properties.name"


# =====================================================
# Interpretation guidance (Section 7.3 of the dissertation)
# NOTE: duplicated across the page modules. Move into components.py.
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
.bley-warning {
    background: #FDECEA;
    border-left: 4px solid #B3261E;
    padding: 10px 14px;
    margin: 8px 0;
    font-size: 0.85rem;
    color: #5F1512;
}
"""


def caveat_banner():
    return ui.div(CAVEAT_TEXT, class_="bley-caveat")


# =====================================================
# Metric definitions
#
# Each metric declares whether a higher value is more or less favourable.
# The colour scale is chosen from that declaration, so deprivation is never
# shaded as though it were a good outcome. Metrics with no inherent
# direction use a neutral sequential scale and say so.
#
# RdYlBu is used in place of RdYlGn because red-green scales are not
# distinguishable for the most common forms of colour vision deficiency
# (WCAG 2.1, success criterion 1.4.1).
# =====================================================

HIGHER_BETTER = "higher_better"
HIGHER_WORSE = "higher_worse"
NEUTRAL = "neutral"

METRICS = {
    "gld": {
        "label": "Good Level of Development (%)",
        "direction": HIGHER_BETTER,
        "decimals": 1,
    },
    "childcare_per_100": {
        "label": "Childcare places per 100 children",
        "direction": HIGHER_BETTER,
        "decimals": 1,
    },
    "ofsted": {
        "label": "Ofsted quality (4 = Outstanding)",
        "direction": HIGHER_BETTER,
        "decimals": 2,
    },
    "fsm": {
        "label": "Free School Meals (%)",
        "direction": HIGHER_WORSE,
        "decimals": 1,
    },
    "idaci": {
        "label": "Income Deprivation (IDACI)",
        "direction": HIGHER_WORSE,
        "decimals": 3,
    },
    "sen": {
        "label": "Special Educational Needs (%)",
        "direction": NEUTRAL,
        "decimals": 1,
    },
    "ethnic_diversity": {
        "label": "Ethnic Diversity Index",
        "direction": NEUTRAL,
        "decimals": 3,
    },
}

DIRECTION_NOTE = {
    HIGHER_BETTER: "Darker blue indicates a more favourable value.",
    HIGHER_WORSE: (
        "Darker red indicates greater disadvantage. The scale is reversed "
        "for this indicator so that less favourable conditions are never "
        "shaded as though they were good outcomes."
    ),
    NEUTRAL: (
        "This indicator has no inherently better or worse direction, so a "
        "single-hue scale is used. Darker shading means a higher value, not "
        "a better or worse one."
    ),
}


def colour_scale(direction):
    if direction == HIGHER_BETTER:
        return "RdYlBu"
    if direction == HIGHER_WORSE:
        return "RdYlBu_r"
    return "Purples"


# =====================================================
# Join validation
#
# px.choropleth_map silently drops rows whose location does not match a
# geojson feature, so a name mismatch would remove boroughs from the map
# with no error. This checks the join up front.
# =====================================================

def validate_join(df):
    geo_names = {
        feature["properties"].get("name")
        for feature in london_geojson.get("features", [])
    }
    data_names = set(df["borough"])
    return {
        "missing_from_map": sorted(data_names - geo_names),
        "missing_from_data": sorted(geo_names - data_names),
    }


# =====================================================
# Borough Explorer Page
# =====================================================

def explorer_page(summary):

    df = summary["df"]
    join = validate_join(df)

    warning = None
    if join["missing_from_map"]:
        warning = ui.div(
            "The following boroughs are in the dataset but do not match a "
            "boundary in the map file, so they are not shaded: "
            + ", ".join(join["missing_from_map"]) + ".",
            class_="bley-warning",
        )

    return ui.nav_panel(

        "📊 Borough Explorer",

        ui.tags.style(CAVEAT_CSS),

        ui.h2("London Borough Explorer"),

        ui.p(
            "Explore how each indicator varies across Greater London. Choose "
            "an indicator to shade the map, and select a borough to see its "
            "full profile against the London average."
        ),

        caveat_banner(),

        *( [warning] if warning is not None else [] ),

        ui.layout_columns(

            ui.input_select(
                "map_metric",
                "Display indicator",
                choices={k: v["label"] for k, v in METRICS.items()},
                selected="gld",
            ),

            ui.input_select(
                "profile_borough",
                "Borough profile",
                choices=sorted(df["borough"].tolist()),
                selected=sorted(df["borough"].tolist())[0],
            ),

            col_widths=(6, 6),

        ),

        ui.output_text("scale_note"),

        ui.br(),

        output_widget("borough_map"),

        ui.hr(),

        ui.h3("Borough Profile"),

        ui.output_table("borough_profile"),

        ui.div(
            "Rank is out of 32 boroughs and is ordered so that rank 1 is the "
            "most favourable value for indicators that have a favourable "
            "direction. Indicators with no inherent direction are ranked from "
            "highest to lowest value only. A rank describes a borough's "
            "position relative to other London boroughs; it is not a "
            "judgement of performance, and many of these indicators reflect "
            "conditions outside a local authority's control.",
            class_="bley-footnote",
        ),
    )


# =====================================================
# Borough Explorer Server
# =====================================================

def explorer_server(input, output, session, summary):

    df = summary["df"]

    @render.text
    def scale_note():
        meta = METRICS[input.map_metric()]
        return DIRECTION_NOTE[meta["direction"]]

    @render_plotly
    def borough_map():

        metric = input.map_metric()
        meta = METRICS[metric]

        hover = {
            key: f":.{value['decimals']}f"
            for key, value in METRICS.items()
            if key in df.columns
        }

        fig = px.choropleth_map(
            df,
            geojson=london_geojson,
            locations="borough",
            featureidkey=FEATURE_KEY,
            color=metric,
            hover_name="borough",
            hover_data=hover,
            labels={k: v["label"] for k, v in METRICS.items()},
            center={"lat": 51.5074, "lon": -0.1278},
            zoom=8.8,
            opacity=0.8,
            map_style="carto-positron",
            color_continuous_scale=colour_scale(meta["direction"]),
        )

        fig.update_layout(
            margin=dict(l=0, r=0, t=0, b=0),
            height=700,
            coloraxis_colorbar=dict(title=meta["label"]),
        )

        return fig

    @render.table
    def borough_profile():

        borough = input.profile_borough()
        row = df[df["borough"] == borough].iloc[0]

        records = []
        for key, meta in METRICS.items():
            if key not in df.columns:
                continue

            value = row[key]
            london = df[key].mean()
            decimals = meta["decimals"]

            ascending = meta["direction"] == HIGHER_WORSE
            rank = int(df[key].rank(ascending=ascending, method="min")[row.name])

            difference = value - london
            if abs(difference) < df[key].std(ddof=1) / 4:
                comparison = "In line with London"
            elif difference > 0:
                comparison = f"{abs(difference):.{decimals}f} above London"
            else:
                comparison = f"{abs(difference):.{decimals}f} below London"

            records.append({
                "Indicator": meta["label"],
                borough: f"{value:.{decimals}f}",
                "London average": f"{london:.{decimals}f}",
                "Compared with London": comparison,
                "Rank of 32": rank if meta["direction"] != NEUTRAL else "-",
            })

        return pd.DataFrame(records)
