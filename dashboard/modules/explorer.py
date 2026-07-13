from shiny import ui, render
from shinywidgets import output_widget, render_plotly

import pandas as pd
import plotly.express as px
import json


# =====================================================
# Load GeoJSON
# =====================================================

with open("data/london_boroughs_wgs84.geojson", "r") as f:
    london_geojson = json.load(f)


# =====================================================
# Borough Explorer Page
# =====================================================

def explorer_page(summary):

    return ui.nav_panel(

        "📊 Borough Explorer",

        ui.h2("London Borough Explorer"),

        ui.p(
            """
            Explore educational outcomes across Greater London.
            Select a metric below to colour the map.
            """
        ),

        ui.input_select(

            "map_metric",

            "Display Metric",

            choices={

                "gld": "Good Level of Development (GLD)",

                "fsm": "Free School Meals (FSM)",

                "sen": "Special Educational Needs (SEN)",

                "idaci": "Income Deprivation (IDACI)",

                "childcare_per_100": "Childcare per 100 Children"

            },

            selected="gld"

        ),

        ui.br(),

        output_widget("borough_map")

    )


# =====================================================
# Borough Explorer Server
# =====================================================

def explorer_server(input, output, session, summary):

    df = summary["df"]

    @render_plotly
    def borough_map():

        metric = input.map_metric()

        fig = px.choropleth_map(
            df,
            geojson=london_geojson,
            locations="borough",
            featureidkey="properties.name",
            color=metric,
            hover_name="borough",
            hover_data={
                "gld": True,
                "fsm": True,
                "sen": True,
                "idaci": True,
                "childcare_per_100": True
            },
            center={
                "lat": 51.5074,
                "lon": -0.1278
            },
            zoom=8.8,
            opacity=0.8,
            map_style="carto-positron",
            color_continuous_scale="RdYlGn"
        )

        fig.update_layout(

            margin=dict(
                l=0,
                r=0,
                t=0,
                b=0
            ),

            height=700

        )

        return fig