import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime

def render_category_analysis_tab(df):
    """
    Renders the Category Analysis tab with visualizations for category performance,
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
    
    # Extract hour for time-based analysis
    df_work["Hour"] = df_work["Timestamp"].dt.hour
    
    # Get top categories by interaction count
    top_categories = df_work["CategoryID"].value_counts().head(10)
    
    # Create category treemap
    category_interactions = df_work.groupby("CategoryID")["BehaviorType"].count().reset_index()
    category_interactions.columns = ["category_id", "interactions"]
    
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
            "total_views": cat_views,
            "view_to_cart_rate": view_to_cart,
            "view_to_buy_rate": view_to_buy,
            "cart_to_buy_rate": cart_to_buy
        })
    
    category_metrics_df = pd.DataFrame(category_metrics)
    
    # Create treemap chart of category popularity
    if not category_interactions.empty:
        fig_treemap = px.treemap(
            category_interactions,
            path=["category_id"],
            values="interactions",
            title="Category Popularity",
            color="interactions",
            color_continuous_scale="Blues",
        )
        fig_treemap.update_layout(height=350)
        st.plotly_chart(fig_treemap, use_container_width=True)
    else:
        st.info("Not enough category data available.")
    
    # Create conversion rate charts and hourly activity
    col1, col2 = st.columns(2)
    
    with col1:
        if not category_metrics_df.empty:
            # Prepare data for bar chart
            conversion_df = pd.melt(
                category_metrics_df, 
                id_vars=["category_id"],
                value_vars=["view_to_cart_rate", "view_to_buy_rate", "cart_to_buy_rate"],
                var_name="conversion_type",
                value_name="rate"
            )
            
            # Make labels more readable
            conversion_df["conversion_type"] = conversion_df["conversion_type"].map({
                "view_to_cart_rate": "View → Cart",
                "view_to_buy_rate": "View → Buy",
                "cart_to_buy_rate": "Cart → Buy"
            })
            
            # Sort by view to buy rate
            top_categories_by_conversion = category_metrics_df.sort_values(
                by="view_to_buy_rate", ascending=False
            )["category_id"].head(5).tolist()
            
            filtered_conv_df = conversion_df[
                conversion_df["category_id"].isin(top_categories_by_conversion)
            ]
            
            fig_conversion = px.bar(
                filtered_conv_df,
                x="category_id",
                y="rate",
                color="conversion_type",
                barmode="group",
                title="Category Conversion Rates",
                labels={
                    "category_id": "Category ID",
                    "rate": "Conversion Rate (%)",
                    "conversion_type": "Conversion Type"
                }
            )
            fig_conversion.update_layout(height=300)
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
        # Hourly activity by category
        if not df_work.empty and "Hour" in df_work.columns:
            # Get top 5 categories
            top_5_cats = top_categories.head(5).index.tolist()
            
            # Prepare data for hourly activity
            hourly_data = []
            
            for cat in top_5_cats:
                cat_df = df_work[df_work["CategoryID"] == cat]
                hourly_counts = cat_df.groupby("Hour").size().reset_index()
                hourly_counts.columns = ["hour", "count"]
                hourly_counts["category_id"] = f"Category {cat}"
                hourly_data.append(hourly_counts)
            
            if hourly_data:
                hourly_df = pd.concat(hourly_data)
                
                fig_hourly = px.line(
                    hourly_df,
                    x="hour",
                    y="count",
                    color="category_id",
                    title="Category Activity by Hour",
                    labels={
                        "hour": "Hour of Day",
                        "count": "Number of Interactions",
                        "category_id": "Category"
                    }
                )
                fig_hourly.update_layout(height=300, xaxis=dict(tickmode='linear', dtick=2))
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
    
    # Category radar chart comparison
    st.markdown('<div class="section-header">Category Comparison</div>', unsafe_allow_html=True)
    
    # Create radar chart for top 5 categories
    if not category_metrics_df.empty:
        top_5_cat_metrics = category_metrics_df.head(5)
        
        # Create radar chart
        fig_radar = go.Figure()
        
        categories = ["View to Cart Rate", "View to Buy Rate", "Cart to Buy Rate", "Total Views"]
        
        # Normalize the values for better visualization
        max_views = top_5_cat_metrics["total_views"].max()
        normalized_views = (top_5_cat_metrics["total_views"] / max_views) * 100
        
        for i, row in top_5_cat_metrics.iterrows():
            fig_radar.add_trace(go.Scatterpolar(
                r=[
                    row["view_to_cart_rate"],
                    row["view_to_buy_rate"],
                    row["cart_to_buy_rate"],
                    normalized_views[i]
                ],
                theta=categories,
                fill='toself',
                name=f"Category {row['category_id']}"
            ))
        
        fig_radar.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100]
                )
            ),
            title="Category Performance Radar",
            height=400
        )
        
        st.plotly_chart(fig_radar, use_container_width=True)
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
    
    # Add insights
    st.markdown("""
    <div class="insight-box">
        <div style="font-weight: bold; margin-bottom: 0.5rem;">Category Insights:</div>
        <p>The analysis shows that different categories have distinct conversion patterns and time-based popularity. 
        Understanding these patterns can help optimize product placement and marketing strategies for each category.</p>
    </div>
    """, unsafe_allow_html=True)