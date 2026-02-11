import plotly.express as px

def sophistication_bar (df,selected_ta):
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
    return fig_soph

def tech_combination (df, selected_ta, format_combo):
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
    return fig_combo

