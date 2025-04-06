import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

def render_product_popularity_tab(df):
    st.markdown('<div class="section-header">Product Popularity Analysis</div>', unsafe_allow_html=True)
    
    # Create a working copy of the dataframe
    df_work = df.copy()
    
    # Clean and check timestamps
    if pd.api.types.is_object_dtype(df_work["Timestamp"]):
        # Extract just the timestamp part using regex
        df_work["Timestamp"] = df_work["Timestamp"].astype(str).str.extract(r'(\d{4}-\d{2}-\d{2}.+)')
        # Convert to datetime
        df_work["Timestamp"] = pd.to_datetime(df_work["Timestamp"], errors='coerce')
    
    # Create date strings for filtering
    df_work["DateOnly"] = df_work["Timestamp"].dt.strftime("%b %d")
    
    # Get unique days and sort them
    day_options = df_work["DateOnly"].dropna().unique().tolist()
    
    # Try to sort chronologically
    try:
        day_options.sort(key=lambda d: pd.to_datetime(d + " 2017", format="%b %d %Y", errors='coerce'))
    except:
        day_options.sort()  # Fallback to alphabetical
    
    # Check if we have valid dates
    if not day_options:
        st.error("No valid dates found in the dataset.")
        return
    
    # Day selector
    selected_day = st.select_slider(
        "Select Day", 
        options=day_options,
        value=day_options[0]
    )

    # Metric selector
    metric_map = {
        "Views": "pv",
        "Cart Additions": "cart",
        "Favorites": "fav",
        "Purchases": "buy"
    }
    selected_display = st.radio("Popularity Metric", list(metric_map.keys()), horizontal=True)
    selected_behavior = metric_map[selected_display]

    # Filter data
    df_filtered = df_work[(df_work["DateOnly"] == selected_day) & 
                         (df_work["BehaviorType"] == selected_behavior)]

    # Check if we have data after filtering
    if df_filtered.empty:
        st.warning(f"No data available for {selected_display} on {selected_day}.")
        return

    # Top 10 products
    top_counts = df_filtered["ItemID"].value_counts().head(10)
    top_products = pd.DataFrame({
        'item_id': top_counts.index,
        'count': top_counts.values
    })

    # Bottom 10 products (excluding items with only 1 interaction to avoid noise)
    bottom_counts = df_filtered["ItemID"].value_counts()
    if len(bottom_counts[bottom_counts > 1]) >= 5:
        bottom_counts = bottom_counts[bottom_counts > 1].tail(10)
    else:
        bottom_counts = bottom_counts.tail(10)
        
    bottom_products = pd.DataFrame({
        'item_id': bottom_counts.index,
        'count': bottom_counts.values
    })

    col1, col2 = st.columns(2)

    with col1:
        if not top_products.empty:
            fig_top = px.bar(top_products, x="count", y="item_id", orientation="h",
                             title=f"Top 10 Products - {selected_display}", 
                             labels={"count": "Interactions", "item_id": "Product ID"})
            fig_top.update_layout(height=350, yaxis=dict(autorange="reversed"))
            st.plotly_chart(fig_top, use_container_width=True)
        else:
            st.info(f"No data for {selected_display} on {selected_day}.")

    with col2:
        if not bottom_products.empty:
            fig_bottom = px.bar(bottom_products, x="count", y="item_id", orientation="h",
                                title=f"Least Popular Products - {selected_display}", 
                                labels={"count": "Interactions", "item_id": "Product ID"})
            fig_bottom.update_layout(height=350, yaxis=dict(autorange="reversed"))
            st.plotly_chart(fig_bottom, use_container_width=True)
        else:
            st.info(f"Not enough data for least popular products.")

    # Product popularity trends
    st.markdown('<div class="section-header">Product Popularity Trends</div>', unsafe_allow_html=True)
    
    # Get the top 5 products overall for this behavior type
    top_5_overall = top_products['item_id'].head(5).tolist()
    
    if top_5_overall:
        # Create time series data for these products
        trend_data = []
        
        for day in day_options:
            day_df = df_work[(df_work["DateOnly"] == day) & 
                           (df_work["BehaviorType"] == selected_behavior)]
            
            for product_id in top_5_overall:
                count = day_df[day_df["ItemID"] == product_id].shape[0]
                trend_data.append({
                    "date": day,
                    "product": f"Product {product_id}",
                    "count": count
                })
        
        trend_df = pd.DataFrame(trend_data)
        
        # Plot time trend
        if not trend_df.empty:
            fig_trend = px.line(
                trend_df, 
                x="date", 
                y="count", 
                color="product",
                title=f"Top 5 Products Popularity Trend - {selected_display}",
                labels={"count": "Number of Interactions", "date": "Date", "product": "Product"}
            )
            fig_trend.update_layout(height=400)
            st.plotly_chart(fig_trend, use_container_width=True)
        else:
            st.info("Not enough data to show product trends over time.")
    else:
        st.info("No products found to show trends.")