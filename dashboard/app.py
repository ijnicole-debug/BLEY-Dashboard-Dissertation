
from shiny import App, ui
import pandas as pd

 
# Import Pages
 

from modules.overview import overview_page, overview_server
from modules.explorer import explorer_page, explorer_server
from modules.relationships import relationships_page, relationships_server
from modules.regression import regression_page, regression_server
from modules.simulator import simulator_page, simulator_server
from modules.about import about_page

 
# Load Data
 

df = pd.read_csv("data/master_dataset.csv")

 
# Summary Statistics
 

summary = {

    "df": df,

    "total_boroughs": df["borough"].nunique(),

    "avg_gld": round(df["gld"].mean(), 1),

    "avg_fsm": round(df["fsm"].mean(), 1),

    "avg_sen": round(df["sen"].mean(), 1),

    "avg_idaci": round(df["idaci"].mean(), 1),

    "highest_gld": df.loc[df["gld"].idxmax()],

    "lowest_gld": df.loc[df["gld"].idxmin()],

    "highest_fsm": df.loc[df["fsm"].idxmax()]

}

 
# User Interface
 

app_ui = ui.page_navbar(

    overview_page(summary),

    explorer_page(summary),

    relationships_page(summary),

    regression_page(summary),

    simulator_page(summary),

    about_page(),

    title="BLEY"

)


# Server

def server(input, output, session):

    overview_server(input, output, session, summary)

    explorer_server(input, output, session, summary)
    
    relationships_server(input, output, session, summary)
    
    regression_server(input, output, session, summary)
    
    simulator_server(input, output, session, summary)
 
# Create App


app = App(app_ui, server)
