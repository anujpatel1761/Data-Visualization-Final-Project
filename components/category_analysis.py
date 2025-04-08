import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Add this at the top of your script or import it where appropriate
category_mapping = {
    4756105: 'Electronics',
    4145813: 'Pet Supplies',
    2355072: 'Clothing',
    3607361: 'Musical Instruments',
    982926: 'Baby Products',
    2520377: 'Garden',
    3010202: 'Books',
    4785201: 'Health & Wellness',
    6823100: 'Toys & Games',
    5551999: 'Tools',
    1000001: 'Automotive',
    1000002: 'Electronics',
    1000003: 'Furniture',
    1000004: 'Grocery',
    1000005: 'Watches',
    1000006: 'Office Supplies',
    1000007: 'Sports',
    1000008: 'Home & Kitchen',
    1000009: 'Shoes',
    1000010: 'Jewelry'
}

def render_category_analysis_tab(df):
    st.markdown('<div class="section-header">Category Analysis</div>', unsafe_allow_html=True)

    df_work = df.copy()
    df_work["CategoryName"] = df_work["CategoryID"].map(category_mapping).fillna("Electronics")

    if pd.api.types.is_object_dtype(df_work["Timestamp"]):
        df_work["Timestamp"] = pd.to_datetime(df_work["Timestamp"], errors='coerce')

    df_work["Hour"] = df_work["Timestamp"].dt.hour
    top_categories = df_work["CategoryID"].value_counts().head(10)

    # Treemap
    category_interactions = df_work.groupby("CategoryName")["BehaviorType"].count().reset_index()
    category_interactions.columns = ["Category", "Interactions"]

    if not category_interactions.empty:
        fig_treemap = px.treemap(
            category_interactions,
            path=["Category"],
            values="Interactions",
            title="Category Popularity",
            color="Interactions",
            color_continuous_scale="Blues"
        )
        fig_treemap.update_layout(height=350)
        st.plotly_chart(fig_treemap, use_container_width=True)
    else:
        st.info("Not enough category data available.")

    # Conversion rates
    category_metrics = []
    for cat_id in top_categories.index:
        cat_df = df_work[df_work["CategoryID"] == cat_id]
        cat_name = category_mapping.get(cat_id, "Electronics")

        views = cat_df[cat_df["BehaviorType"] == "pv"].shape[0]
        carts = cat_df[cat_df["BehaviorType"] == "cart"].shape[0]
        buys = cat_df[cat_df["BehaviorType"] == "buy"].shape[0]

        view_to_cart = (carts / views * 100) if views > 0 else 0
        view_to_buy = (buys / views * 100) if views > 0 else 0
        cart_to_buy = (buys / carts * 100) if carts > 0 else 0

        category_metrics.append({
            "Category": cat_name,
            "Total Views": views,
            "View → Cart": view_to_cart,
            "View → Buy": view_to_buy,
            "Cart → Buy": cart_to_buy
        })

    category_metrics_df = pd.DataFrame(category_metrics)

    col1, col2 = st.columns(2)

    with col1:
        if not category_metrics_df.empty:
            melted = pd.melt(
                category_metrics_df,
                id_vars="Category",
                value_vars=["View → Cart", "View → Buy", "Cart → Buy"],
                var_name="Conversion Type",
                value_name="Rate"
            )
            top_categories_sorted = category_metrics_df.sort_values(by="View → Buy", ascending=False)["Category"].head(5)
            filtered = melted[melted["Category"].isin(top_categories_sorted)]

            fig_conversion = px.bar(
                filtered,
                x="Category",
                y="Rate",
                color="Conversion Type",
                barmode="group",
                title="Category Conversion Rates",
                labels={"Rate": "Conversion Rate (%)"}
            )
            fig_conversion.update_layout(height=300)
            st.plotly_chart(fig_conversion, use_container_width=True)
        else:
            st.warning("Not enough conversion data available.")

    with col2:
        top_5_cats = top_categories.head(5).index.tolist()
        hourly_data = []
        for cat_id in top_5_cats:
            cat_df = df_work[df_work["CategoryID"] == cat_id]
            hourly_counts = cat_df.groupby("Hour").size().reset_index(name="Count")
            hourly_counts["Category"] = category_mapping.get(cat_id, "Other")
            hourly_data.append(hourly_counts)

        if hourly_data:
            hourly_df = pd.concat(hourly_data)

            fig_hourly = px.line(
                hourly_df,
                x="Hour",
                y="Count",
                color="Category",
                title="Category Activity by Hour",
                labels={"Hour": "Hour of Day", "Count": "Interactions"}
            )
            fig_hourly.update_layout(height=300, xaxis=dict(tickmode='linear', dtick=2))
            st.plotly_chart(fig_hourly, use_container_width=True)
        else:
            st.info("Not enough hourly data.")

    st.markdown('<div class="section-header">Category Comparison</div>', unsafe_allow_html=True)

    if not category_metrics_df.empty:
        top_5 = category_metrics_df.head(5)
        fig_radar = go.Figure()
        labels = ["View → Cart", "View → Buy", "Cart → Buy", "Total Views"]
        max_views = top_5["Total Views"].max()
        norm_views = (top_5["Total Views"] / max_views) * 100

        for i, row in top_5.iterrows():
            fig_radar.add_trace(go.Scatterpolar(
                r=[
                    row["View → Cart"],
                    row["View → Buy"],
                    row["Cart → Buy"],
                    norm_views.iloc[i]
                ],
                theta=labels,
                fill='toself',
                name=row["Category"]
            ))

        fig_radar.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
            title="Category Performance Radar",
            height=400
        )
        st.plotly_chart(fig_radar, use_container_width=True)
    else:
        st.info("Not enough data to display radar chart.")

    st.markdown("""
    <div class="insight-box">
        <div style="font-weight: bold; margin-bottom: 0.5rem;">Category Insights:</div>
        <p>The analysis shows that different categories have distinct conversion patterns and time-based popularity. 
        Understanding these patterns can help optimize product placement and marketing strategies for each category.</p>
    </div>
    """, unsafe_allow_html=True)
