import plotly.express as px;

def motiv_asset (df,selected_root, selected_asset):

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
    return fig_root_asset
