import plotly.express as px
def actor_protection(df,s4_ta, s4_prot):
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
    return fig_actor_protection
