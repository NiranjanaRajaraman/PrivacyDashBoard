import plotly.express as px

def heatmap(df, selected_ta):
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
    return fig_heatmap
