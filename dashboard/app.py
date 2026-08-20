import sys
from pathlib import Path

from shiny import App, ui
import pandas as pd


# =====================================================
# Import path
#
# uvicorn's reloader does not always place the working directory on
# sys.path, so the app directory is added explicitly. This also makes the
# app importable from any working directory and on ShinyApps.io.
# =====================================================

APP_DIR = Path(__file__).resolve().parent
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))


# =====================================================
# Import pages
# =====================================================

from modules.overview import overview_page, overview_server
from modules.explorer import explorer_page, explorer_server
from modules.relationships import relationships_page, relationships_server
from modules.regression import regression_page, regression_server
from modules.recommendations import recommendations_page, recommendations_server
from modules.simulator import simulator_page, simulator_server
from modules.about import about_page


# =====================================================
# Load data
#
# Paths are anchored to this file rather than the working directory, so
# the app behaves the same locally and on ShinyApps.io.
# =====================================================

DATA_PATH = APP_DIR / "data" / "master_dataset.csv"

df = pd.read_csv(DATA_PATH)


# =====================================================
# Startup validation
#
# Fail loudly at startup rather than producing wrong figures if the
# master dataset is regenerated with a different structure.
# =====================================================

REQUIRED_COLUMNS = [
    "la_code", "borough", "gld", "fsm", "sen", "idaci", "ofsted",
    "inspection_coverage", "total_places", "under5", "childcare_per_100",
    "ethnic_diversity", "average_house_price",
]

missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
if missing:
    raise ValueError(
        f"master_dataset.csv is missing required columns: {missing}"
    )

if len(df) != 32:
    raise ValueError(
        f"Expected 32 boroughs in master_dataset.csv, found {len(df)}."
    )

if df[REQUIRED_COLUMNS].isna().any().any():
    incomplete = df[REQUIRED_COLUMNS].isna().sum()
    raise ValueError(
        "master_dataset.csv contains missing values in: "
        f"{list(incomplete[incomplete > 0].index)}"
    )

# Ofsted is stored on a rescaled 1-4 scale where 4 is Outstanding.
# A value below 2 would indicate the reversal in 06_clean_ofsted has not
# been applied, which would silently invert every reading of the variable.
if df["ofsted"].mean() < 2:
    raise ValueError(
        "Ofsted quality values look unreversed (mean below 2). Check that "
        "06_clean_ofsted applies the 5 - score rescaling and excludes "
        "ungraded providers."
    )


# =====================================================
# Summary statistics
#
# Rounding is applied at display time in the page modules, not here, so
# that no module is handed a value that has already lost precision.
# =====================================================

summary = {

    "df": df,

    "total_boroughs": df["borough"].nunique(),

    "avg_gld": df["gld"].mean(),

    "avg_fsm": df["fsm"].mean(),

    "avg_sen": df["sen"].mean(),

    "avg_idaci": df["idaci"].mean(),

    "avg_ofsted": df["ofsted"].mean(),

    "avg_childcare": df["childcare_per_100"].mean(),

    "highest_gld": df.loc[df["gld"].idxmax()],

    "lowest_gld": df.loc[df["gld"].idxmin()],

    "highest_fsm": df.loc[df["fsm"].idxmax()],

}


# =====================================================
# Shared styling
#
# The theme lives in style.css. A minimal fallback for the
# interpretation banner is injected inline as well.
# =====================================================

CSS_CANDIDATES = [
    APP_DIR / "www" / "style.css",
    APP_DIR / "style.css",
    APP_DIR / "assets" / "style.css",
    APP_DIR / "static" / "style.css",
]

CSS_PATH = next((p for p in CSS_CANDIDATES if p.exists()), None)
if CSS_PATH is None:
    raise FileNotFoundError(
        "style.css not found. Looked in: "
        + ", ".join(str(p) for p in CSS_CANDIDATES)
    )

CAVEAT_FALLBACK = """
.bley-caveat {
    background: #FFF4E5;
    border-left: 4px solid #C77700;
    padding: 10px 14px;
    margin: 8px 0 16px 0;
    font-size: 0.9rem;
    color: #4A3000;
}
"""


# =====================================================
# User interface
# =====================================================

app_ui = ui.page_navbar(

    overview_page(summary),

    explorer_page(summary),

    relationships_page(summary),

    regression_page(summary),

    recommendations_page(summary),

    simulator_page(summary),

    about_page(summary),

    title="BLEY",

    header=ui.tags.head(
        ui.tags.style(CAVEAT_FALLBACK),
        ui.include_css(CSS_PATH),
    ),

)


# =====================================================
# Server
# =====================================================

def server(input, output, session):

    overview_server(input, output, session, summary)

    explorer_server(input, output, session, summary)

    relationships_server(input, output, session, summary)

    regression_server(input, output, session, summary)

    recommendations_server(input, output, session, summary)

    simulator_server(input, output, session, summary)


# =====================================================
# Create app
# =====================================================

app = App(app_ui, server)
