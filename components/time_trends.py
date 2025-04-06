import pandas as pd
import plotly.express as px
import streamlit as st


def render_time_trends_tab(df):
    st.markdown('<div class="section-header">Time-Based Analysis</div>', unsafe_allow_html=True)

    # DAILY TRENDS
    df['Date'] = df['Timestamp'].dt.date
    daily_counts = df.groupby("Date").size().reset_index(name="Interactions")
    fig_daily = px.line(daily_counts, x="Date", y="Interactions", title="Daily Activity Trends")
    fig_daily.update_layout(height=300)
    st.plotly_chart(fig_daily, use_container_width=True)

    # HOURLY ACTIVITY HEATMAP
    st.markdown('<div class="section-header">Hourly Activity Patterns</div>', unsafe_allow_html=True)

    df["Hour"] = df["Timestamp"].dt.hour
    df["Day"] = df["Timestamp"].dt.date
    hourly_counts = df.groupby(["Day", "Hour"]).size().reset_index(name="Count")
    fig_hourly = px.density_heatmap(
        hourly_counts,
        x="Hour",
        y="Day",
        z="Count",
        title="Hourly Activity Heatmap",
        color_continuous_scale="Viridis"
    )
    fig_hourly.update_layout(height=350)
    st.plotly_chart(fig_hourly, use_container_width=True)

    # WEEKDAY VS WEEKEND
    st.markdown('<div class="section-header">Weekday vs Weekend Behavior</div>', unsafe_allow_html=True)

    df["Weekday"] = df["Timestamp"].dt.dayofweek
    df["DayType"] = df["Weekday"].apply(lambda x: "Weekend" if x >= 5 else "Weekday")
    daytype_counts = df.groupby(["DayType", "BehaviorType"]).size().reset_index(name="Count")
    fig_daytype = px.bar(
        daytype_counts,
        x="BehaviorType",
        y="Count",
        color="DayType",
        barmode="group",
        title="Weekday vs Weekend Behaviors"
    )
    fig_daytype.update_layout(height=350)
    st.plotly_chart(fig_daytype, use_container_width=True)

    # HOURLY CONVERSION RATE
    st.markdown('<div class="section-header">Hourly Conversion Rate</div>', unsafe_allow_html=True)

    df["Hour"] = df["Timestamp"].dt.hour
    hourly_behavior = df.groupby(["Hour", "BehaviorType"]).size().unstack(fill_value=0)
    hourly_behavior["ConversionRate"] = (hourly_behavior.get("buy", 0) / hourly_behavior.get("pv", 1)) * 100

    fig_conv = px.line(
        hourly_behavior.reset_index(),
        x="Hour",
        y="ConversionRate",
        title="Hourly Conversion Rate (%)"
    )
    fig_conv.update_layout(height=300, yaxis_title="Conversion Rate (%)")
    st.plotly_chart(fig_conv, use_container_width=True)
