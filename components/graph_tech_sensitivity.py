import plotly.express as px
def tech_sensitivity(df_exploded, selected_scores,selected_section5_tech):
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
    return fig_tech_sens