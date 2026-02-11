import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output, callback
import plotly.graph_objects as go
import numpy as np
from components.data_handler import load_and_clean_data, get_sophistication_signal, format_combo
from components.graph_actor import create_main_bar, create_network_graph
from components.graph_motiv_asset import motiv_asset
from components.graph_heatmap import heatmap
from components.graph_actor_protection import actor_protection
from components.graph_tech_sensitivity import tech_sensitivity
from components.graph_motiv_exposure import motiv_exposure
from components.graph_tech_sophistication import sophistication_bar,tech_combination

# ==============================================================================
# 1. CONFIGURATION & CONSTANTS
# ==============================================================================
FILE_NAME = "incidents-export-2026-02-01-22-09-03.csv"

PROFESSIONAL_COLORS = [
    "#2563eb", "#1e3a8a", "#64748b", "#16a34a", "#f59e0b", "#dc2626",
]

ACCESSIBLE_PALETTE = [
    "#0072B2", "#D55E00", "#009E73", "#E69F00", "#56B4E9", "#F0E442", 
    "#CC79A7", "#000000", "#332288", "#88CCEE", "#44AA99", "#117733", 
    "#999933", "#DDCC77", "#CC6677", "#882255", "#1170aa", "#fc7d0b", 
    "#a3acb9", "#57606c", "#5fa2ce", "#c85200", "#7b919e", "#a87d9f"
]

# =================================================================
# --- INITIAL LOAD ---
# =================================================================
df, df_exploded, total_records, month_name = load_and_clean_data(FILE_NAME)
# Sophistication Logic
df["Sophistication_Category"] = df["Techniques Used"].apply(get_sophistication_signal)

# Unique values for Dropdowns
motivations = sorted(df["Root Cause (Why)"].fillna("Unknown").unique())
exposure_levels = sorted(
    df["Data exposure score"]
    .fillna(-1)
    .astype(str)
    .replace("-1.0", "Unknown")
    .replace("-1", "Unknown")
    .unique()
)

techniques = sorted(df_exploded["Techniques Used"].dropna().unique())
threat_actor_counts = df["Threat Actor"].value_counts().head(15).index.tolist()
root_causes = sorted(df["Root Cause (Why)"].dropna().unique())
asset_types = sorted(df["Asset Type"].dropna().unique())
protection_states = sorted(df["Data Protection State"].unique())
sensitivity_options = sorted(df_exploded["Sensitivity_Label"].unique())

# ==============================================================================
# 5. APP INITIALIZATION & LAYOUT
# ==============================================================================
app = Dash(__name__)

app.layout = html.Div([
    # --- HEADER ---
    html.Div([
        html.H1("Incident Analysis Dashboard", className="header"),
        html.P("Comprehensive analysis of cyber security incidents and risk matrices.", className="header-description"),
    ]),
    # =================================================================
    # SUMMARY CARDS 
    # =================================================================
    html.Div([
        html.Div([
            html.H3(f"{total_records:,}", className="summary-main"),
            html.P("Total Records Analyzed", className="summary-sub ")
        ], className="summary-card"),
        
        html.Div([
            html.H3(month_name, className="summary-main"),
            html.P("Reporting Period", className="summary-sub")
        ], className="summary-card"),
    ], className="summary"),
    # =================================================================
    # --- SECTION 1: Threat Actor & Techniques ---
    # =================================================================
    html.Div([
        html.H2("Threat Actor vs Techniques", className="section-title"),
        html.Div([
            html.Div([
                html.Label("Filter by Threat Actor", style={'fontWeight': 'bold'}),
                dcc.Dropdown(
                    id="threat-actor-filter",
                    options=[{"label": ta, "value": ta} for ta in threat_actor_counts],
                    value=None, multi=True, placeholder="All Threat Actors"
                )
            ], className="dropdown-left"),

            html.Div([
                html.Label("Filter by Technique", style={'fontWeight': 'bold'}),
                dcc.Dropdown(
                    id="technique-filter",
                    options=[{"label": "Unknown", "value": "Unknown"}] + [{"label": t, "value": t} for t in techniques],
                    value=None, multi=True, searchable=True, placeholder="Search & select techniques"
                )
            ], className="dropdown-right"),
        ], className="dropdown-container"),
        dcc.Graph(id="main-viz", style={'height': '500px'}),
    ], className="section"),
    
    # --- SECTION: Network Graph ---

    html.Div([
        html.H2("Threat Actor & Technique Network", className="section-title"),
        html.P("Visualizing the top 10 relationships between actors and their methods.", className="section-description"),
        dcc.Graph(id='network-graph')
    ], className="section network-container"),

    # =================================================================
    # --- SECTION 2: Motivation & Asset Type ---
    # =================================================================
    html.Div([
        html.H2("Assets Impacted by Motivation", className="section-title"),
        html.Div([
            html.Div([
                html.Label("Motivation", style={'fontWeight': 'bold'}),
                dcc.Dropdown(
                    id="root-cause-filter",
                    options=[{"label": rc, "value": rc} for rc in root_causes],
                    value=None, multi=True, placeholder="All Root Causes"
                )
            ], className="dropdown-left"),

            html.Div([
                html.Label("Asset Type", style={'fontWeight': 'bold'}),
                dcc.Dropdown(
                    id="asset-type-filter",
                    options=[{"label": at, "value": at} for at in asset_types],
                    value=None, multi=True, placeholder="All Asset Types"
                )
            ], className="dropdown-right"),
        ], className="dropdown-container"),
        dcc.Graph(id="root-asset-viz", style={'height': '500px'}),
    ], className="section"),
    # =================================================================
    # --- SECTION 3: Heatmap ---
    # =================================================================
    html.Div([
        html.H2("Risk Matrix: Protection vs Sensitivity", className="section-title"),
        dcc.Graph(id="protection-sensitivity-heatmap", style={'height':'500px'})
    ], className="section"),

    # =================================================================
    # --- SECTION 4: Actor vs Protection ---
    # =================================================================
    html.Div([
        html.H2("Threat Actor and Data Protection State Analysis", className="section-title"),
        html.Div([
            html.Div([
                html.Label("Filter by Threat Actor", style={'fontWeight': 'bold'}),
                dcc.Dropdown(
                    id="s4-actor-filter",
                    options=[{"label": ta, "value": ta} for ta in threat_actor_counts],
                    multi=True, placeholder="All Threat Actors"
                )
            ], className="dropdown-left"),

            html.Div([
                html.Label("Filter by Protection State", style={'fontWeight': 'bold'}),
                dcc.Dropdown(
                    id="s4-protection-filter",
                    options=[{"label": ps, "value": ps} for ps in protection_states],
                    multi=True, placeholder="All Protection States"
                )
            ], className="dropdown-right"),
        ], className="dropdown-container"),
        dcc.Graph(id="actor-protection-viz", style={'height': '500px'}),
    ], className="section"),
    # =================================================================
    # --- SECTION 5: Technique Distribution ---
    # =================================================================
    html.Div([
        html.H2("Technique & Sensitivity Distribution", className="section-title"),
        html.Div([
            html.Div([
                html.Label("Filter by Sensitivity Score", style={'fontWeight': 'bold'}),
                dcc.Dropdown(
                    id='sensitivity-score-filter',
                    options=[{'label': i, 'value': i} for i in sensitivity_options],
                    multi=True, placeholder="All Sensitivity Scores"
                )
            ], className="dropdown-left"), 

            html.Div([
                html.Label("Filter by Technique", style={'fontWeight': 'bold'}),
                dcc.Dropdown(
                    id="section5-technique-filter",
                    options=[{"label": "Unknown", "value": "Unknown"}] + [{"label": t, "value": t} for t in techniques],
                    value=None, multi=True, searchable=True, placeholder="Search & select techniques"
                )
            ], className="dropdown-right"),
        ], className="dropdown-container"),
        dcc.Graph(id="tech-sens-distribution-bar", style={'height': '500px'})
    ], className="section"),
    # =================================================================
    # --- SECTION 6: Rose Plot ---
    # =================================================================
    html.Div([
        html.H2("Data Exposure Levels by Attack Motivation", className="section-title"),
        html.P("Radius represents incident volume. Segments show the breakdown of exposure scores.", className="section-title-description"),
        html.Div([
            html.Div([
                html.Label("Filter by Motivation", style={'fontWeight': 'bold'}),
                dcc.Dropdown(
                    id="rose-motivation-filter",
                    options=[{"label": m, "value": m} for m in motivations],
                    multi=True, searchable=True, placeholder="All Motivations"
                )
            ], className="dropdown-left"),

            html.Div([
                html.Label("Filter by Exposure Level", style={'fontWeight': 'bold'}),
                dcc.Dropdown(
                    id="rose-exposure-filter",
                    options=[{"label": e, "value": e} for e in exposure_levels],
                    multi=True, placeholder="All Exposure Levels"
                )
            ], className="dropdown-right"),
        ], className="dropdown-container"),
        dcc.Graph(id="motivation-exposure-rose", style={'height': '600px'})
    ], className="section"),
    # =================================================================
    # --- SECTION 7: Attacker Sophistication ---
    # =================================================================
    html.Div([
        html.H2("Attacker Techniques", className="section-title"),
        html.P("Distribution of technique density based on their combination of usage", className="section-title-description"),
        dcc.Graph(id="sophistication-bar-viz", style={'height': '450px'}),
        dcc.Graph(id="technique-combinations-viz", style={'height': '500px'})
    ], className="section"),

], className="app-container")

# ==============================================================================
# 6. CALLBACKS
# ==============================================================================
@callback(
    [
        Output("main-viz", "figure"),
        Output("network-graph", "figure"),
        Output("root-asset-viz", "figure"),
        Output("protection-sensitivity-heatmap", "figure"),
        Output("actor-protection-viz", "figure"),
        Output("tech-sens-distribution-bar", "figure"),
        Output("motivation-exposure-rose", "figure"),
        Output("sophistication-bar-viz", "figure"),
        Output("technique-combinations-viz", "figure")
    ],
    [
        Input("threat-actor-filter", "value"),
        Input("technique-filter", "value"),
        Input("root-cause-filter", "value"),
        Input("asset-type-filter", "value"),
        Input("section5-technique-filter", "value"),
        Input("rose-motivation-filter","value"),
        Input("rose-exposure-filter","value"),
        Input("s4-actor-filter", "value"),      
        Input("s4-protection-filter", "value"),
        Input("sensitivity-score-filter", "value"),
    ]
)
def update_dashboard(selected_ta, selected_tech, selected_root, selected_asset, 
                     selected_section5_tech, rose_motivation_filter, rose_exposure_filter, 
                     s4_ta, s4_prot, selected_scores):

    # --- 6.1 Data Filtering: Main Viz ---
    f_df_exp = df_exploded.copy()
    fig = create_main_bar(f_df_exp, df_exploded,selected_ta, selected_tech, ACCESSIBLE_PALETTE)

    # --- 6.2 Network graph ---
    fig_network = create_network_graph(df_exploded, ACCESSIBLE_PALETTE)

    # --- 6.3 Motivation/Asset Viz ---
    fig_root_asset = motiv_asset (df,selected_root, selected_asset)

    # --- 6.4 Heatmap ---
    fig_heatmap = heatmap (df, selected_ta)

    # --- 6.5 Security Posture ---
    fig_actor_protection = actor_protection(df,s4_ta, s4_prot)

    # --- 6.6 Tech/Sens Distribution (Section 5) ---
    fig_tech_sens= tech_sensitivity(df_exploded, selected_scores,selected_section5_tech)

    # --- 6.7 Rose Plot ---
    fig_rose= motiv_exposure(df,rose_motivation_filter,rose_exposure_filter)
    
    # --- 6.8 Sophistication Bar ---
    fig_soph= sophistication_bar (df,selected_ta)

    # --- 6.9 Technique Combinations ---
    fig_combo= tech_combination (df, selected_ta, format_combo)
    
    return fig, fig_network, fig_root_asset, fig_heatmap, fig_actor_protection, fig_tech_sens, fig_rose, fig_soph, fig_combo

# ==============================================================================
# 7. RUN APP
# ==============================================================================
if __name__ == "__main__":
    app.run(debug=True, port=8051)