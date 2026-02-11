import plotly.express as px
import numpy as np
def motiv_exposure(df,rose_motivation_filter,rose_exposure_filter):
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
    return fig_rose
