import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output, callback
import os
import networkx as nx
import plotly.graph_objects as go
import numpy as np

# ==============================================================================
# 1. CONFIGURATION & CONSTANTS
# ==============================================================================
file_name = "incidents-export-2026-02-01-22-09-03.csv"

PROFESSIONAL_COLORS = [
    "#2563eb", "#1e3a8a", "#64748b", "#16a34a", "#f59e0b", "#dc2626",
]

ACCESSIBLE_PALETTE = [
    "#0072B2", "#D55E00", "#009E73", "#E69F00", "#56B4E9", "#F0E442", 
    "#CC79A7", "#000000", "#332288", "#88CCEE", "#44AA99", "#117733", 
    "#999933", "#DDCC77", "#CC6677", "#882255", "#1170aa", "#fc7d0b", 
    "#a3acb9", "#57606c", "#5fa2ce", "#c85200", "#7b919e", "#a87d9f"
]

# ==============================================================================
# 2. DATA LOADING & INITIAL CLEANING
# ==============================================================================
df = pd.read_csv(
    file_name, 
    sep=";", 
    encoding="utf-8-sig"
    )

# Metadata for UI
total_records = len(df)
month_name = os.path.splitext(file_name)[0].capitalize()

# Basic Normalization
df["Data Protection State"] = df["Data Protection State"].fillna("No Protection")
df["Techniques Used"] = df["Techniques Used"].fillna("Unknown")
df["Techniques Used"] = df["Techniques Used"].astype(str).str.split(",")

# Exploded dataframe for technique-specific analysis
df_exploded = df.explode("Techniques Used")
df_exploded["Techniques Used"] = df_exploded["Techniques Used"].str.strip()

# ==============================================================================
# 3. HELPER FUNCTIONS
# ==============================================================================
def get_sophistication_signal(val):
    if pd.isna(val) is True or val is None:
        return "Unknown Technique"
    
    text = ",".join(val) if isinstance(val, list) else str(val)
    text = text.strip().lower()
    
    if text in ['', 'nan', 'unknown', 'none']:
        return "Unknown Technique"
    
    techs = [t.strip() for t in text.split(",") if t.strip()]
    count = len(techs)
    
    if count == 0:
        return "Unknown Technique"
    elif count == 1:
        return "Single Technique"
    elif 2 <= count <= 3:
        return "Multi-Technique (2–3)"
    else:
        return "Multi-Stage (4+)"

def format_combo(val):
    if pd.isna(val) is True: return "Unknown"
    if isinstance(val, list):
        techs = sorted([str(t).strip() for t in val if str(t).strip()])
    else:
        techs = sorted([t.strip() for t in str(val).split(",") if t.strip()])
    return " + ".join(techs) if techs else "Unknown"

# ==============================================================================
# 4. FEATURE ENGINEERING & PRE-PROCESSING
# ==============================================================================
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

# Sensitivity Labeling
df_exploded["Sensitivity_Label"] = df_exploded["Data Sensitivity score"].astype(str)
df_exploded.loc[df_exploded["Data Sensitivity score"] == -1, "Sensitivity_Label"] = "-1 (Score Unknown)"
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

    # --- SUMMARY CARDS ---
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

    # --- SECTION 1: Threat Actor & Techniques ---
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

    # --- SECTION 2: Motivation & Asset Type ---
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

    # --- SECTION 3: Heatmap ---
    html.Div([
        html.H2("Risk Matrix: Protection vs Sensitivity", className="section-title"),
        dcc.Graph(id="protection-sensitivity-heatmap", style={'height':'500px'})
    ], className="section"),

    # --- SECTION 4: Actor vs Protection ---
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

    # --- SECTION 5: Technique Distribution ---
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

    # --- SECTION 6: Rose Plot ---
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

    # --- SECTION 7: Attacker Sophistication ---
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
    if selected_ta:
        f_df_exp = f_df_exp[f_df_exp["Threat Actor"].isin(selected_ta)]
    if selected_tech:
        f_df_exp = f_df_exp[f_df_exp["Techniques Used"].isin(selected_tech)]

    ta_tech_counts = f_df_exp.groupby(["Threat Actor", "Techniques Used"]).size().reset_index(name="Count")
    fig = px.bar(
        ta_tech_counts, x="Threat Actor", y="Count", color="Techniques Used",
        barmode="group", title="Technique Usage by Threat Actor",
        color_discrete_sequence=ACCESSIBLE_PALETTE, template="plotly_white"
    )
    fig.update_yaxes(type="log", title="Incident Count (log scale)", dtick=1)

    # --- 6.2 Network Graph ---
    top_pairs = df_exploded.groupby(['Threat Actor', 'Techniques Used']).size().nlargest(10).reset_index(name='counts')
    
    idx = (top_pairs["Threat Actor"] == "Unknown")
    top_pairs.loc[idx, "Threat Actor"] = "Unknown (Threat Actor)"
    idx = (top_pairs["Techniques Used"] == "Unknown")
    top_pairs.loc[idx, "Techniques Used"] = "Unknown (Technique Used)"
    
    threat_actor_unique = set(top_pairs["Threat Actor"])
    techniques_unique = set(top_pairs["Techniques Used"])

    G = nx.Graph()
    for ta in threat_actor_unique:
        for teq in techniques_unique:
            combination_count = top_pairs[(top_pairs["Threat Actor"] == ta) & 
                                        (top_pairs["Techniques Used"] == teq)]["counts"]
            combination_count = combination_count.item() if len(combination_count) > 0 else 0
            G.add_node(ta, type='Threat Actor')
            G.add_node(teq, type='Technique Used', count=combination_count)
            G.add_edge(ta, teq, weight=combination_count)

    pos = {}
    ta_list = sorted(list(threat_actor_unique))
    teq_list = sorted(list(techniques_unique))

    for i, ta in enumerate(ta_list):
        pos[ta] = np.array([0, i / (max(1, len(ta_list)-1)) if len(ta_list) > 1 else 0.5])
    for i, teq in enumerate(teq_list):
        pos[teq] = np.array([1, i / (max(1, len(teq_list)-1)) if len(teq_list) > 1 else 0.5])

    edge_traces, edge_annotations = [], []
    for edge in G.edges(data=True):
        u, v = edge[0], edge[1]
        x0, y0 = pos[u]
        x1, y1 = pos[v]
        weight = edge[2]['weight']
        if weight > 0:
            edge_traces.append(go.Scatter(x=[x0, x1, None], y=[y0, y1, None],
                               line=dict(width=5, color='rgba(200, 210, 230, 0.5)'),
                               hoverinfo='none', mode='lines'))
            edge_annotations.append(dict(x=(x0 + x1) / 2, y=(y0 + y1) / 2,
                                    text=f"<b>{weight}</b>", showarrow=False,
                                    font=dict(size=14, color="black"),
                                    bgcolor=ACCESSIBLE_PALETTE[5], bordercolor="white",
                                    borderwidth=1, borderpad=4, opacity=0.9))

    actor_trace = go.Scatter(x=[pos[ta][0] for ta in ta_list], y=[pos[ta][1] for ta in ta_list],
                             mode='markers+text', text=ta_list, textposition="middle left",
                             textfont=dict(size=16, color=ACCESSIBLE_PALETTE[0]),
                             marker=dict(size=50, color=ACCESSIBLE_PALETTE[0], line=dict(width=2, color='black')),
                             hoverinfo='none')

    tech_trace = go.Scatter(x=[pos[teq][0] for teq in teq_list], y=[pos[teq][1] for teq in teq_list],
                            mode='markers+text', text=teq_list, textposition="middle right",
                            textfont=dict(size=16, color=ACCESSIBLE_PALETTE[2]),
                            marker=dict(size=30, color=ACCESSIBLE_PALETTE[2], line=dict(width=2, color='black')),
                            hoverinfo='none')

    fig_network = go.Figure(data=edge_traces + [actor_trace, tech_trace],
                            layout=go.Layout(annotations=edge_annotations,
                            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-0.8, 1.8]),
                            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-0.1, 1.1]),
                            margin=dict(l=10, r=10, t=10, b=10), template="plotly_white", height=600,
                            autosize=True, showlegend=False))

    # --- 6.3 Motivation/Asset Viz ---
    root_df = df.copy()
    if selected_root:
        root_df = root_df[root_df["Root Cause (Why)"].isin(selected_root)]
    if selected_asset:
        root_df = root_df[root_df["Asset Type"].isin(selected_asset)]

    root_df["Root Cause (Why)"] = root_df["Root Cause (Why)"].fillna("Unknown")
    root_df["Asset Type"] = root_df["Asset Type"].fillna("Unknown")
    root_asset_counts = root_df.groupby(["Root Cause (Why)", "Asset Type"]).size().reset_index(name="Count")
    
    fig_root_asset = px.bar(
        root_asset_counts, x="Root Cause (Why)", y="Count", color="Asset Type",
        barmode="group", title="Incidents by Motivation and Asset Type", 
        color_discrete_sequence=px.colors.qualitative.Safe, template="plotly_white"
    )
    fig_root_asset.update_yaxes(type="log", title="Incident Count (log scale)", dtick=1)

    # --- 6.4 Heatmap ---
    heatmap_df = df.copy()
    if selected_ta:
        heatmap_df = heatmap_df[heatmap_df["Threat Actor"].isin(selected_ta)]
    heatmap_df["Data Sensitivity score"] = heatmap_df["Data Sensitivity score"].fillna(-1)

    pivot = heatmap_df.pivot_table(index='Data Protection State', columns='Data Sensitivity score', aggfunc='size', fill_value=0)
    x_labels = [f"{int(c)} (score unknown)" if c == -1 else str(int(c)) for c in pivot.columns]

    fig_heatmap = px.imshow(
        pivot, text_auto=True, aspect="auto", x=x_labels, y=pivot.index,
        labels=dict(x="Sensitivity Score", y="Protection State", color="Count"),
        color_continuous_scale="algae"
    )

    # --- 6.5 Security Posture (Section 4) ---
    f_df_s4 = df.copy()
    if s4_ta:
        f_df_s4 = f_df_s4[f_df_s4["Threat Actor"].isin(s4_ta)]
    if s4_prot:
        f_df_s4 = f_df_s4[f_df_s4["Data Protection State"].isin(s4_prot)]
    
    ap_counts = f_df_s4.groupby(["Threat Actor", "Data Protection State"]).size().reset_index(name="Count")
    ap_counts['Percentage'] = ap_counts.groupby('Threat Actor')['Count'].transform(lambda x: (x / x.sum()) * 100)
    
    fig_actor_protection = px.bar(
        ap_counts, x="Threat Actor", y="Count", color="Data Protection State",
        hover_data={"Percentage": ":.1f%"}, barmode="group",
        title="Security Posture per Threat Actor", color_discrete_sequence=px.colors.qualitative.Safe,
        template="plotly_white"
    )
    fig_actor_protection.update_traces(hovertemplate="<b>%{x}</b><br>Protection State = %{fullData.name}<br>Count=%{y}<br>Percentage=%{customdata[0]:.1f}%<extra></extra>")
    fig_actor_protection.update_yaxes(type="log", title="Incident Count (log scale)", dtick=1)

    # --- 6.6 Tech/Sens Distribution (Section 5) ---
    dff = df_exploded.copy()
    if selected_scores:
        dff = dff[dff["Sensitivity_Label"].isin(selected_scores)]
    if selected_section5_tech:
        dff = dff[dff["Techniques Used"].isin(selected_section5_tech)]

    dist_df = dff.groupby(["Techniques Used", "Sensitivity_Label"]).size().reset_index(name="Incident Count")
    total_counts = dist_df.groupby("Techniques Used")["Incident Count"].sum().sort_values(ascending=False).index
    
    fig_tech_sens = px.bar(
        dist_df, x="Techniques Used", y="Incident Count", color="Sensitivity_Label",
        title="Count of Incidents by Technique and Sensitivity Level",
        category_orders={"Techniques Used": total_counts}, 
        color_discrete_sequence=px.colors.qualitative.Safe, template="plotly_white", barmode="group" 
    )
    fig_tech_sens.update_yaxes(type="log", title="Incident Count (log scale)", dtick=1)

    # --- 6.7 Rose Plot ---
    rose_df = df.copy()
    rose_df["Motivation"] = rose_df["Root Cause (Why)"].fillna("Unknown")
    if rose_motivation_filter:
        rose_df = rose_df[rose_df["Motivation"].isin(rose_motivation_filter)]
    
    rose_df["Data exposure score"] = rose_df["Data exposure score"].fillna(-1)
    rose_df["Exposure Label"] = rose_df["Data exposure score"].astype(str).replace("-1.0", "Unknown").replace("-1", "Unknown")
    if rose_exposure_filter:
        rose_df = rose_df[rose_df["Exposure Label"].isin(rose_exposure_filter)]

    rose_counts = rose_df.groupby(["Motivation", "Exposure Label"]).size().reset_index(name="Actual_Count")
    rose_counts["Display_Size"] = np.sqrt(rose_counts["Actual_Count"])

    fig_rose = px.bar_polar(
        rose_counts, r="Display_Size", theta="Motivation", color="Exposure Label",
        template="plotly_white", custom_data=["Actual_Count"], title="Motivation vs Exposure",
        color_discrete_sequence=px.colors.qualitative.Safe, start_angle=90
    )
    fig_rose.update_traces(hovertemplate="<b>%{theta}</b><br>Score: %{fullData.name}<br>Incidents: %{customdata[0]}<extra></extra>")
    fig_rose.update_layout(height=600, polar=dict(radialaxis=dict(showticklabels=False), angularaxis=dict(tickmode='array', tickvals=rose_counts["Motivation"].unique(), direction='clockwise')))

    # --- 6.8 Sophistication Bar ---
    soph_df = df.copy()
    if selected_ta:
        soph_df = soph_df[soph_df["Threat Actor"].isin(selected_ta)]

    s_actor_counts = soph_df.groupby("Sophistication_Category").size().reset_index(name="Incident Count")
    category_order = ["Unknown Technique", "Single Technique", "Multi-Technique (2–3)", "Multi-Stage (4+)"]

    fig_soph = px.bar(
        s_actor_counts, x="Sophistication_Category", y="Incident Count", color="Sophistication_Category",
        title="Incident Count by Sophistication Level", category_orders={"Sophistication_Category": category_order},
        color_discrete_sequence=px.colors.qualitative.Safe 
    )
    fig_soph.update_yaxes(type="log", title="Incident Count (log)", dtick=1)

    # --- 6.9 Technique Combinations ---
    combo_df = df.copy()
    if selected_ta:
        combo_df = combo_df[combo_df["Threat Actor"].isin(selected_ta)]
    
    combo_df["Combo_String"] = combo_df["Techniques Used"].apply(format_combo)
    sophisticated_combos = combo_df[combo_df["Sophistication_Category"].isin(["Multi-Technique (2–3)", "Multi-Stage (4+)"])]
    
    combo_counts = sophisticated_combos["Combo_String"].value_counts().reset_index().head(10)
    combo_counts.columns = ["Combination", "Incident Count"]

    fig_combo = px.bar(
        combo_counts, y="Combination", x="Incident Count", orientation='h',
        title="Top Technique Combinations", color_discrete_sequence=px.colors.qualitative.Safe,
        template="plotly_white", text_auto=True 
    )
    fig_combo.update_xaxes(type="log", title="Incident Count (Log Scale)")
    fig_combo.update_layout(showlegend=False, yaxis={'categoryorder':'total ascending'}, margin=dict(l=350), height=550)

    return fig, fig_network, fig_root_asset, fig_heatmap, fig_actor_protection, fig_tech_sens, fig_rose, fig_soph, fig_combo

# ==============================================================================
# 7. RUN APP
# ==============================================================================
if __name__ == "__main__":
    app.run(debug=True, port=8051)