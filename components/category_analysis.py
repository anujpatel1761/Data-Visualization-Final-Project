import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime

def render_category_analysis_tab(df):
    """
    Renders the Category Analysis tab with improved visualizations for category performance,
    conversion rates, and time-based activity.
    
    Parameters:
    df (pandas.DataFrame): The dataframe with e-commerce data
    """
    st.markdown('<div class="section-header">Category Analysis</div>', unsafe_allow_html=True)
    
    # Create a working copy of the dataframe
    df_work = df.copy()
    
    # Clean timestamps if needed
    if pd.api.types.is_object_dtype(df_work["Timestamp"]):
        df_work["Timestamp"] = df_work["Timestamp"].astype(str).str.extract(r'(\d{4}-\d{2}-\d{2}.+)')
        df_work["Timestamp"] = pd.to_datetime(df_work["Timestamp"], errors='coerce')
    
    # Extract time components for analysis
    df_work["Hour"] = df_work["Timestamp"].dt.hour
    df_work["Day"] = df_work["Timestamp"].dt.day_name()
    
    # Get top categories by interaction count
    top_categories = df_work["CategoryID"].value_counts().head(10)
    
    # Create a mapping dictionary for category labels
    category_labels = {cat_id: f"Category {cat_id}" for cat_id in top_categories.index}
    
    # Add formatted column with category labels
    df_work["CategoryLabel"] = df_work["CategoryID"].map(
        lambda x: category_labels.get(x, f"Category {x}") if x in top_categories.index else "Other Categories"
    )
    
    # Create improved category treemap
    category_interactions = df_work.groupby(["CategoryID", "CategoryLabel", "BehaviorType"]).size().reset_index(name="Count")
    
    # Calculate total interactions per category for treemap
    category_totals = category_interactions.groupby(["CategoryID", "CategoryLabel"])["Count"].sum().reset_index()
    
    # Add behavior counts for hover information
    category_behavior_counts = category_interactions.pivot_table(
        index=["CategoryID", "CategoryLabel"],
        columns="BehaviorType",
        values="Count",
        fill_value=0
    ).reset_index()
    
    # Merge with totals
    category_totals = category_totals.merge(category_behavior_counts, on=["CategoryID", "CategoryLabel"])
    
    # Sort by total interactions
    category_totals = category_totals.sort_values("Count", ascending=False).head(10)
    
    # Add hover text with behavior breakdown
    category_totals["HoverText"] = category_totals.apply(
        lambda row: f"<b>{row['CategoryLabel']}</b><br>" +
                   f"Total Interactions: {row['Count']:,}<br>" +
                   f"Page Views: {row.get('pv', 0):,}<br>" +
                   f"Add to Cart: {row.get('cart', 0):,}<br>" +
                   f"Favorites: {row.get('fav', 0):,}<br>" +
                   f"Purchases: {row.get('buy', 0):,}",
        axis=1
    )
    
    # Create improved treemap chart of category popularity
    if not category_totals.empty:
        fig_treemap = px.treemap(
            category_totals,
            path=["CategoryLabel"],
            values="Count",
            title="Top 10 Category Popularity",
            color="Count",
            color_continuous_scale="Blues",
            hover_data=["Count"],
            custom_data=["HoverText"]
        )
        
        # Customize hover template
        fig_treemap.update_traces(
            hovertemplate="%{customdata[0]}<extra></extra>",
            textinfo="label+value"
        )
        
        fig_treemap.update_layout(
            height=400,
            margin=dict(t=50, l=25, r=25, b=25),
            coloraxis_colorbar=dict(
                title="Interactions",
                tickformat=",",
            )
        )
        st.plotly_chart(fig_treemap, use_container_width=True)
    else:
        st.info("Not enough category data available.")
    
    # Add explanatory text
    st.markdown("""
    <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin-top: 10px; margin-bottom: 20px;">
        <p><strong>About the Treemap:</strong> The size of each box represents the total number of interactions for that category. 
        Darker colors indicate more popular categories. <em>Hover over each box to see detailed behavior breakdowns.</em></p>
    </div>
    """, unsafe_allow_html=True)
    
    # Calculate conversion rates for each category
    category_metrics = []
    
    for cat_id in top_categories.index:
        cat_df = df_work[df_work["CategoryID"] == cat_id]
        
        # Count different behaviors
        cat_views = cat_df[cat_df["BehaviorType"] == "pv"].shape[0]
        cat_carts = cat_df[cat_df["BehaviorType"] == "cart"].shape[0]
        cat_favs = cat_df[cat_df["BehaviorType"] == "fav"].shape[0]
        cat_buys = cat_df[cat_df["BehaviorType"] == "buy"].shape[0]
        
        # Calculate rates
        view_to_cart = (cat_carts / cat_views * 100) if cat_views > 0 else 0
        view_to_buy = (cat_buys / cat_views * 100) if cat_views > 0 else 0
        cart_to_buy = (cat_buys / cat_carts * 100) if cat_carts > 0 else 0
        
        category_metrics.append({
            "category_id": cat_id,
            "category_label": category_labels.get(cat_id, f"Category {cat_id}"),
            "total_views": cat_views,
            "total_carts": cat_carts,
            "total_buys": cat_buys,
            "view_to_cart_rate": view_to_cart,
            "view_to_buy_rate": view_to_buy,
            "cart_to_buy_rate": cart_to_buy
        })
    
    category_metrics_df = pd.DataFrame(category_metrics)
    
    # Create conversion rate charts and hourly activity
    col1, col2 = st.columns(2)
    
    with col1:
        if not category_metrics_df.empty:
            # Get top 5 categories by view-to-buy conversion rate
            top_categories_by_conversion = category_metrics_df.sort_values(
                by="view_to_buy_rate", ascending=False
            ).head(5)
            
            # Create a comparison bar chart
            fig_conversion = go.Figure()
            
            # Add traces for each conversion metric
            fig_conversion.add_trace(go.Bar(
                x=top_categories_by_conversion["category_label"],
                y=top_categories_by_conversion["view_to_cart_rate"],
                name="View → Cart",
                marker_color="#36A2EB",
                text=[f"{val:.1f}%" for val in top_categories_by_conversion["view_to_cart_rate"]],
                textposition="auto"
            ))
            
            fig_conversion.add_trace(go.Bar(
                x=top_categories_by_conversion["category_label"],
                y=top_categories_by_conversion["cart_to_buy_rate"],
                name="Cart → Buy",
                marker_color="#4BC0C0",
                text=[f"{val:.1f}%" for val in top_categories_by_conversion["cart_to_buy_rate"]],
                textposition="auto"
            ))
            
            fig_conversion.add_trace(go.Bar(
                x=top_categories_by_conversion["category_label"],
                y=top_categories_by_conversion["view_to_buy_rate"],
                name="View → Buy (Overall)",
                marker_color="#FF6384",
                text=[f"{val:.1f}%" for val in top_categories_by_conversion["view_to_buy_rate"]],
                textposition="auto"
            ))
            
            # Update layout
            fig_conversion.update_layout(
                title="Top 5 Categories by Conversion Rate",
                xaxis_title="Category",
                yaxis_title="Conversion Rate (%)",
                legend_title="Conversion Type",
                height=350,
                barmode="group",
                bargap=0.15,
                bargroupgap=0.1,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                ),
                yaxis=dict(
                    range=[0, max(
                        top_categories_by_conversion["view_to_cart_rate"].max(),
                        top_categories_by_conversion["cart_to_buy_rate"].max(),
                        top_categories_by_conversion["view_to_buy_rate"].max()
                    ) * 1.1]  # Add 10% padding
                )
            )
            
            st.plotly_chart(fig_conversion, use_container_width=True)
        else:
            st.markdown("""
            <div class="chart-placeholder">
                <div style="text-align: center;">
                    <div style="font-size: 2rem; margin-bottom: 0.5rem;">📊</div>
                    <div style="font-weight: bold;">Category Conversion Rates</div>
                    <div style="color: #7f8c8d; margin-top: 0.5rem;">No data available</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        # Improved hourly activity by category
# Replace the hourly activity chart section in render_category_analysis_tab with this code:

        # Improved hourly activity by category
        if not df_work.empty and "Hour" in df_work.columns:
            # Get top 5 categories
            top_5_cats = top_categories.head(5).index.tolist()
            
            # Prepare data for hourly activity
            hourly_data = []
            
            for cat in top_5_cats:
                cat_df = df_work[df_work["CategoryID"] == cat]
                hourly_counts = cat_df.groupby("Hour").size().reset_index()
                hourly_counts.columns = ["hour", "count"]
                hourly_counts["category_id"] = cat
                hourly_counts["category_label"] = category_labels.get(cat, f"Category {cat}")
                hourly_data.append(hourly_counts)
            
            if hourly_data:
                hourly_df = pd.concat(hourly_data)
                
                # Create time period labels
                def time_period(hour):
                    if 0 <= hour <= 5:
                        return "Night (12AM-6AM)"
                    elif 6 <= hour <= 11:
                        return "Morning (6AM-12PM)"
                    elif 12 <= hour <= 17:
                        return "Afternoon (12PM-6PM)"
                    else:
                        return "Evening (6PM-12AM)"
                
                hourly_df["time_period"] = hourly_df["hour"].apply(time_period)
                
                # Create improved line chart
                fig_hourly = px.line(
                    hourly_df,
                    x="hour",
                    y="count",
                    color="category_label",
                    title="Category Activity by Hour of Day",
                    labels={
                        "hour": "Hour of Day",
                        "count": "Number of Interactions",
                        "category_label": "Category"
                    },
                    markers=True,
                    hover_data=["time_period"]
                )
                
                # Add time period bands with annotations as separate shapes and annotations
                # instead of using the annotation_position parameter
                time_periods = [
                    {"name": "Night", "start": 0, "end": 5, "color": "rgba(128, 128, 128, 0.1)"},
                    {"name": "Morning", "start": 6, "end": 11, "color": "rgba(255, 220, 0, 0.1)"},
                    {"name": "Afternoon", "start": 12, "end": 17, "color": "rgba(255, 165, 0, 0.1)"},
                    {"name": "Evening", "start": 18, "end": 23, "color": "rgba(70, 130, 180, 0.1)"}
                ]
                
                for period in time_periods:
                    # Add the rectangle without annotation
                    fig_hourly.add_vrect(
                        x0=period["start"], 
                        x1=period["end"] + 0.99,  # Add 0.99 to cover the full hour
                        fillcolor=period["color"],
                        layer="below",
                        line_width=0
                    )
                    
                    # Add a separate annotation for the time period
                    fig_hourly.add_annotation(
                        x=(period["start"] + period["end"]) / 2,  # Center of the time period
                        y=1.05,  # Position above the plot
                        text=period["name"],
                        showarrow=False,
                        xref="x",
                        yref="paper",
                        font=dict(size=10)
                    )
                
                # Update layout
                fig_hourly.update_layout(
                    height=350,
                    xaxis=dict(
                        tickmode='array',
                        tickvals=list(range(0, 24, 3)),  # Show every 3 hours
                        ticktext=[f"{i:02d}:00" for i in range(0, 24, 3)]
                    ),
                    yaxis=dict(title="Interactions"),
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="right",
                        x=1
                    ),
                    hovermode="x unified"
                )
                
                st.plotly_chart(fig_hourly, use_container_width=True)
            else:
                st.info("Not enough hourly data available for categories.")
        else:
            st.markdown("""
            <div class="chart-placeholder">
                <div style="text-align: center;">
                    <div style="font-size: 2rem; margin-bottom: 0.5rem;">⏱️</div>
                    <div style="font-weight: bold;">Category Activity by Hour</div>
                    <div style="color: #7f8c8d; margin-top: 0.5rem;">No data available</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    # Add explanatory text for the charts
    st.markdown("""
    <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin-top: 10px; margin-bottom: 20px;">
        <p><strong>Understanding These Charts:</strong></p>
        <ul>
            <li><strong>Conversion Rate Chart:</strong> Shows how well each category converts at different stages of the funnel. Higher "View → Buy" rates indicate better overall conversion.</li>
            <li><strong>Hourly Activity Chart:</strong> Reveals when each category receives the most activity throughout the day. Background colors indicate different times of day (morning, afternoon, evening, night).</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    # Improved category radar chart comparison
    st.markdown('<div class="section-header">Category Performance Comparison</div>', unsafe_allow_html=True)
    
    # Create radar chart for top 5 categories
    if not category_metrics_df.empty:
        # Sort by overall performance (sum of normalized metrics)
        category_metrics_df["overall_performance"] = (
            category_metrics_df["view_to_cart_rate"] + 
            category_metrics_df["view_to_buy_rate"] * 2 +  # Weight view-to-buy more
            category_metrics_df["cart_to_buy_rate"]
        )
        
        top_5_cat_metrics = category_metrics_df.sort_values(
            by="overall_performance", ascending=False
        ).head(5)
        
        # Create radar chart with better labels and formatting
        fig_radar = go.Figure()
        
        categories = [
            "Page View to Cart %", 
            "Page View to Purchase %", 
            "Cart to Purchase %", 
            "Total Page Views"
        ]
        
        # Normalize the values for better visualization
        max_views = top_5_cat_metrics["total_views"].max()
        normalized_views = (top_5_cat_metrics["total_views"] / max_views) * 100
        
        # Define a color palette
        colors = ['#FF6384', '#36A2EB', '#4BC0C0', '#FFCE56', '#9966FF']
        
        for i, (_, row) in enumerate(top_5_cat_metrics.iterrows()):
            fig_radar.add_trace(go.Scatterpolar(
                r=[
                    row["view_to_cart_rate"],
                    row["view_to_buy_rate"],
                    row["cart_to_buy_rate"],
                    normalized_views.iloc[i]
                ],
                theta=categories,
                fill='toself',
                name=row["category_label"],
                line=dict(color=colors[i % len(colors)]),
                fillcolor=colors[i % len(colors)].replace(')', ', 0.2)').replace('rgb', 'rgba')
            ))
        
        fig_radar.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100],
                    ticksuffix="%"
                ),
                angularaxis=dict(
                    direction="clockwise"
                )
            ),
            title={
                'text': "Top 5 Categories Performance Comparison",
                'x': 0.5,
                'xanchor': 'center'
            },
            height=500,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.1,
                xanchor="center",
                x=0.5
            )
        )
        
        st.plotly_chart(fig_radar, use_container_width=True)
        
        # Add explanation for the radar chart
        st.markdown("""
        <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin-top: 10px;">
            <p><strong>How to Read the Radar Chart:</strong> Each category is represented by a different color. 
            The further a point extends from the center, the better that category performs on that metric. 
            The ideal category would extend to the outer edge on all metrics.</p>
            <ul>
                <li><strong>Page View to Cart %:</strong> How often users add items to cart after viewing</li>
                <li><strong>Page View to Purchase %:</strong> Overall conversion from viewing to buying</li>
                <li><strong>Cart to Purchase %:</strong> How often cart additions lead to purchases</li>
                <li><strong>Total Page Views:</strong> Relative popularity by page views (normalized)</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="chart-placeholder" style="height: 350px;">
            <div style="text-align: center;">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">📊</div>
                <div style="font-weight: bold;">Category Performance Radar</div>
                <div style="color: #7f8c8d; margin-top: 0.5rem;">No data available</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Add actionable insights
    st.markdown("""
    <div style="background-color: #eaf4fb; padding: 20px; border-radius: 5px; margin-top: 20px; border-left: 5px solid #3498db;">
        <h4 style="margin-top: 0; color: #2c3e50;">💡 Category Insights</h4>
        <p>Based on the analysis of category performance data:</p>
        <ul>
            <li><strong>High-Converting Categories:</strong> Categories with high View→Purchase rates should be featured prominently on the homepage and in marketing campaigns.</li>
            <li><strong>Time-Optimized Promotions:</strong> Schedule category-specific promotions during their peak activity hours to maximize visibility.</li>
            <li><strong>Improvement Opportunities:</strong> Categories with high page views but low conversion rates may need better product descriptions, more competitive pricing, or improved imagery.</li>
            <li><strong>Cart Abandonment:</strong> Categories with high Cart→Purchase drop-offs might benefit from targeted cart recovery emails or limited-time checkout incentives.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)