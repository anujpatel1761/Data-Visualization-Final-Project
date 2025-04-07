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

    # HOURLY ACTIVITY HEATMAP - IMPROVED
    st.markdown('<div class="section-header">Hourly Activity Patterns</div>', unsafe_allow_html=True)

    # Extract hour and add a formatted time label
    df["Hour"] = df["Timestamp"].dt.hour
    df["Hour_Label"] = df["Hour"].apply(lambda x: f"{x:02d}:00")
    
    # Extract day and format it better
    df["Day"] = df["Timestamp"].dt.date
    df["Day_Formatted"] = df["Timestamp"].dt.strftime("%a, %b %d")  # e.g., "Mon, Nov 27"
    
    # Extract behavior counts by hour and day
    hourly_counts = df.groupby(["Day", "Day_Formatted", "Hour", "Hour_Label"]).size().reset_index(name="Count")
    
    # Get behavior type counts for tooltips
    behavior_counts = df.groupby(["Day", "Hour", "BehaviorType"]).size().reset_index(name="BehaviorCount")
    behavior_pivot = behavior_counts.pivot_table(
        index=["Day", "Hour"], 
        columns="BehaviorType", 
        values="BehaviorCount",
        fill_value=0
    ).reset_index()
    
    # Merge the behavior data
    hourly_counts = hourly_counts.merge(behavior_pivot, on=["Day", "Hour"], how="left")
    
    # Fill NaN values for behavior types that might be missing
    for behavior in ["pv", "cart", "fav", "buy"]:
        if behavior not in hourly_counts.columns:
            hourly_counts[behavior] = 0
    
    # Create hover text with detailed information
    hourly_counts["HoverText"] = hourly_counts.apply(
        lambda row: f"<b>{row['Day_Formatted']}, {row['Hour_Label']}</b><br>" +
                   f"Total Activity: {row['Count']:,}<br>" +
                   f"Page Views: {row.get('pv', 0):,}<br>" +
                   f"Add to Cart: {row.get('cart', 0):,}<br>" +
                   f"Favorites: {row.get('fav', 0):,}<br>" +
                   f"Purchases: {row.get('buy', 0):,}",
        axis=1
    )
    
    # Custom time period labels for context
    def time_period_label(hour):
        if 5 <= hour <= 8:
            return "Early Morning"
        elif 9 <= hour <= 11:
            return "Morning"
        elif 12 <= hour <= 14:
            return "Lunch Time"
        elif 15 <= hour <= 17:
            return "Afternoon"
        elif 18 <= hour <= 21:
            return "Evening"
        else:
            return "Night Time"
    
    hourly_counts["TimePeriod"] = hourly_counts["Hour"].apply(time_period_label)
    
    # Create custom colorscale with meaningful labels
    import plotly.graph_objects as go
    
    # Calculate 4-hour activity blocks for annotations
    time_periods = ["Early Morning (5-8)", "Morning (9-11)", "Lunch (12-14)", 
                    "Afternoon (15-17)", "Evening (18-21)", "Night (22-4)"]
    
    fig_hourly = go.Figure(data=go.Heatmap(
        z=hourly_counts["Count"],
        x=hourly_counts["Hour"],
        y=hourly_counts["Day_Formatted"],
        colorscale="Viridis",
        hoverinfo="text",
        hovertext=hourly_counts["HoverText"],
        text=hourly_counts["Count"].apply(lambda x: f"{x:,}"),
        texttemplate="%{text}",
        showscale=True
    ))
    
    # Add time period annotations
    time_ranges = [(5,8), (9,11), (12,14), (15,17), (18,21), (22,4)]
    
    for i, (period, (start, end)) in enumerate(zip(time_periods, time_ranges)):
        # Skip if outside our range
        if start > 23 or end > 23:
            continue
            
        # Calculate the center position for the annotation
        center_x = (start + end) / 2
        
        # Add annotation at the top
        fig_hourly.add_annotation(
            x=center_x,
            y=1.05,  # Position above the heatmap
            xref="x",
            yref="paper",
            text=period,
            showarrow=False,
            font=dict(size=10),
            bgcolor="rgba(255,255,255,0.7)",
            bordercolor="black",
            borderwidth=1,
            borderpad=2
        )
    
    # Update layout for better readability
    fig_hourly.update_layout(
        title={
            'text': 'User Activity by Hour of Day',
            'x': 0.5,
            'xanchor': 'center'
        },
        xaxis={
            'title': 'Hour of Day',
            'tickmode': 'array',
            'tickvals': list(range(0, 24, 2)),  # Show every 2 hours
            'ticktext': [f"{i:02d}:00" for i in range(0, 24, 2)]
        },
        yaxis={
            'title': 'Date',
            'categoryorder': 'category ascending'  # Keep days in chronological order
        },
        height=400,
        margin=dict(l=10, r=10, t=50, b=60),
        coloraxis_colorbar=dict(
            title="Activity Count",
            ticksuffix=" actions"
        )
    )
    
    st.plotly_chart(fig_hourly, use_container_width=True)
    
    # Add a clear insight box
    st.markdown("""
    <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin-bottom: 20px;">
        <h4 style="margin-top: 0;">📊 Hourly Activity Insights</h4>
        <p>This heatmap reveals when users are most active on the platform:</p>
        <ul>
            <li><strong>Peak Activity:</strong> Midday hours (around 10 AM - 2 PM) show the highest activity levels</li>
            <li><strong>Weekend Patterns:</strong> Notice how weekend activity patterns differ from weekdays</li>
            <li><strong>Night Activity:</strong> Lower activity during late night/early morning hours (11 PM - 5 AM)</li>
        </ul>
        <p><em>Hover over cells to see detailed behavior breakdowns for each hour.</em></p>
    </div>
    """, unsafe_allow_html=True)

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