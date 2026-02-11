import plotly.express as px
import plotly.graph_objects as go
import networkx as nx
import numpy as np

# --- 6.1 Data Filtering: Main Viz ---
def create_main_bar(f_df_exp, df_exploded,selected_ta, selected_tech, ACCESSIBLE_PALETTE):

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
    return fig

def create_network_graph(df_exploded, ACCESSIBLE_PALETTE):

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
    return fig_network
