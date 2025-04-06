import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime

def render_user_behavior_tab(df):
    """
    Renders the User Behavior tab with visualizations for user journeys,
    user segments, and session analysis.
    
    Parameters:
    df (pandas.DataFrame): The dataframe with e-commerce data
    """
    st.markdown('<div class="section-header">User Behavior Analysis</div>', unsafe_allow_html=True)
    
    # Create a working copy of the dataframe
    df_work = df.copy()
    
    # Clean timestamps if needed
    if pd.api.types.is_object_dtype(df_work["Timestamp"]):
        df_work["Timestamp"] = df_work["Timestamp"].astype(str).str.extract(r'(\d{4}-\d{2}-\d{2}.+)')
        df_work["Timestamp"] = pd.to_datetime(df_work["Timestamp"], errors='coerce')
    
    # Create Sankey diagram data for user journeys
    user_journeys = create_user_journey_sankey(df_work)
    if user_journeys:
        st.plotly_chart(user_journeys, use_container_width=True)
    else:
        st.markdown("""
        <div class="chart-placeholder" style="height: 350px;">
            <div style="text-align: center;">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">🔄</div>
                <div style="font-weight: bold;">User Behavior Flow</div>
                <div style="color: #7f8c8d; margin-top: 0.5rem;">Not enough journey data available</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # User segments section
    st.markdown('<div class="section-header">User Segments</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # User segments by behavior
        user_segments = create_user_segments_chart(df_work)
        if user_segments:
            st.plotly_chart(user_segments, use_container_width=True)
        else:
            st.markdown("""
            <div class="chart-placeholder">
                <div style="text-align: center;">
                    <div style="font-size: 2rem; margin-bottom: 0.5rem;">👥</div>
                    <div style="font-weight: bold;">User Segments by Behavior</div>
                    <div style="color: #7f8c8d; margin-top: 0.5rem;">Not enough data for segmentation</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        # Session duration vs conversion (products viewed vs purchase probability)
        session_analysis = create_session_analysis_chart(df_work)
        if session_analysis:
            st.plotly_chart(session_analysis, use_container_width=True)
        else:
            st.markdown("""
            <div class="chart-placeholder">
                <div style="text-align: center;">
                    <div style="font-size: 2rem; margin-bottom: 0.5rem;">⏱️</div>
                    <div style="font-weight: bold;">Products Viewed vs Purchase Rate</div>
                    <div style="color: #7f8c8d; margin-top: 0.5rem;">Not enough session data available</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    # Generate dynamic insights based on data analysis
    insights = generate_behavior_insights(df_work)
    st.markdown(f"""
    <div class="insight-box">
        <div style="font-weight: bold; margin-bottom: 0.5rem;">User Behavior Insights:</div>
        <p>{insights}</p>
    </div>
    """, unsafe_allow_html=True)


def create_user_journey_sankey(df):
    """
    Creates a Sankey diagram showing user journey paths through the sales funnel.
    
    Parameters:
    df (pandas.DataFrame): The dataframe with user behavior data
    
    Returns:
    plotly.graph_objects.Figure or None: The Sankey diagram, or None if not enough data
    """
    # Need to have enough users with multiple behaviors to create a journey
    user_behavior_counts = df.groupby("UserID")["BehaviorType"].nunique()
    users_with_multiple_behaviors = user_behavior_counts[user_behavior_counts > 1].index.tolist()
    
    if len(users_with_multiple_behaviors) < 10:
        return None
    
    # Filter for users with multiple behaviors and sort by timestamp
    journey_df = df[df["UserID"].isin(users_with_multiple_behaviors)].sort_values(["UserID", "Timestamp"])
    
    # Create source-target pairs for the Sankey diagram
    journey_pairs = []
    
    for user_id in users_with_multiple_behaviors:
        user_sequence = journey_df[journey_df["UserID"] == user_id]["BehaviorType"].tolist()
        
        # Take the first 3 steps of the journey at most (to avoid complexity)
        user_sequence = user_sequence[:3]
        
        if len(user_sequence) > 1:
            for i in range(len(user_sequence) - 1):
                journey_pairs.append((user_sequence[i], user_sequence[i+1]))
    
    if not journey_pairs:
        return None
    
    # Count occurrences of each pair
    pair_counts = {}
    for source, target in journey_pairs:
        pair_key = (source, target)
        pair_counts[pair_key] = pair_counts.get(pair_key, 0) + 1
    
    # Create lists for Sankey diagram
    behavior_types = ["pv", "cart", "fav", "buy"]
    behavior_labels = {"pv": "Page View", "cart": "Add to Cart", "fav": "Favorite", "buy": "Purchase"}
    
    # Create node indices mapping
    node_indices = {behavior: i for i, behavior in enumerate(behavior_types)}
    
    # Prepare Sankey data
    sources = []
    targets = []
    values = []
    
    for (source, target), count in pair_counts.items():
        if source in node_indices and target in node_indices:
            sources.append(node_indices[source])
            targets.append(node_indices[target])
            values.append(count)
    
    # Create the Sankey diagram
    if not sources or not targets or not values:
        return None
        
    node_labels = [behavior_labels.get(behavior, behavior) for behavior in behavior_types]
    
    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=15,
            thickness=20,
            line=dict(color="black", width=0.5),
            label=node_labels,
            color=["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728"]
        ),
        link=dict(
            source=sources,
            target=targets,
            value=values,
            color="rgba(200, 200, 200, 0.4)"
        )
    )])
    
    fig.update_layout(
        title="User Journey Flow",
        height=350,
        font=dict(size=12)
    )
    
    return fig


def create_user_segments_chart(df):
    """
    Creates a chart showing user segments based on their behavior patterns.
    
    Parameters:
    df (pandas.DataFrame): The dataframe with user behavior data
    
    Returns:
    plotly.graph_objects.Figure or None: The user segments chart, or None if not enough data
    """
    # Count how many users have each type of behavior
    user_behaviors = {}
    for behavior in ["pv", "cart", "fav", "buy"]:
        users_with_behavior = df[df["BehaviorType"] == behavior]["UserID"].unique()
        user_behaviors[behavior] = set(users_with_behavior)
    
    # Define user segments
    segments = {
        "Browsers": user_behaviors["pv"] - user_behaviors["cart"] - user_behaviors["fav"] - user_behaviors["buy"],
        "Cart Abandoners": (user_behaviors["cart"] - user_behaviors["buy"]),
        "Wishlisters": (user_behaviors["fav"] - user_behaviors["buy"]),
        "Purchasers": user_behaviors["buy"]
    }
    
    # Calculate segment sizes
    segment_sizes = {segment: len(users) for segment, users in segments.items()}
    
    # Check if we have enough data
    if sum(segment_sizes.values()) < 10:
        return None
    
    # Create the segment chart
    segment_df = pd.DataFrame({
        "Segment": list(segment_sizes.keys()),
        "Users": list(segment_sizes.values())
    })
    
    # Add percentage
    total_users = segment_df["Users"].sum()
    segment_df["Percentage"] = segment_df["Users"] / total_users * 100
    segment_df["SegmentLabel"] = segment_df.apply(
        lambda row: f"{row['Segment']}: {row['Percentage']:.1f}%", axis=1
    )
    
    fig = px.pie(
        segment_df,
        names="SegmentLabel",
        values="Users",
        title="User Segments by Behavior",
        color="Segment",
        color_discrete_map={
            "Browsers": "#1f77b4",
            "Cart Abandoners": "#ff7f0e",
            "Wishlisters": "#2ca02c",
            "Purchasers": "#d62728"
        }
    )
    
    fig.update_layout(height=300)
    fig.update_traces(textposition='inside', textinfo='percent')
    
    return fig


def create_session_analysis_chart(df):
    """
    Creates a chart showing the relationship between products viewed and purchase probability.
    
    Parameters:
    df (pandas.DataFrame): The dataframe with user behavior data
    
    Returns:
    plotly.graph_objects.Figure or None: The session analysis chart, or None if not enough data
    """
    # Count products viewed and purchases per user
    user_product_views = df[df["BehaviorType"] == "pv"].groupby("UserID")["ItemID"].nunique().reset_index()
    user_product_views.columns = ["UserID", "ProductsViewed"]
    
    # Get users who purchased
    users_who_purchased = df[df["BehaviorType"] == "buy"]["UserID"].unique()
    
    # Add purchase flag to user_product_views
    user_product_views["Purchased"] = user_product_views["UserID"].isin(users_who_purchased)
    
    # Check if we have enough data
    if len(user_product_views) < 5:
        return None
    
    # Create product view bins more safely
    user_product_views["ViewCategory"] = "1 product"  # Default category
    
    # Assign categories based on products viewed
    user_product_views.loc[user_product_views["ProductsViewed"] == 2, "ViewCategory"] = "2 products"
    user_product_views.loc[(user_product_views["ProductsViewed"] >= 3) & 
                          (user_product_views["ProductsViewed"] <= 5), "ViewCategory"] = "3-5 products"
    user_product_views.loc[(user_product_views["ProductsViewed"] >= 6) & 
                          (user_product_views["ProductsViewed"] <= 10), "ViewCategory"] = "6-10 products"
    user_product_views.loc[user_product_views["ProductsViewed"] > 10, "ViewCategory"] = "11+ products"
    
    # Define the order of categories for plotting
    category_order = ["1 product", "2 products", "3-5 products", "6-10 products", "11+ products"]
    
    # Calculate purchase rate by view category
    purchase_rate = user_product_views.groupby("ViewCategory")["Purchased"].mean().reset_index()
    purchase_rate["PurchaseRate"] = purchase_rate["Purchased"] * 100
    
    # Count users in each category
    category_counts = user_product_views["ViewCategory"].value_counts().reset_index()
    category_counts.columns = ["ViewCategory", "UserCount"]
    
    # Merge rates and counts
    view_analysis = pd.merge(purchase_rate, category_counts, on="ViewCategory")
    
    # Ensure we have all categories in the right order
    view_analysis = view_analysis[view_analysis["ViewCategory"].isin(category_order)]
    
    # Sort by the predefined order
    view_analysis["OrderIndex"] = view_analysis["ViewCategory"].apply(lambda x: category_order.index(x) if x in category_order else 999)
    view_analysis = view_analysis.sort_values("OrderIndex")
    
    # Create the chart
    fig = px.bar(
        view_analysis,
        x="ViewCategory",
        y="PurchaseRate",
        title="Products Viewed vs Purchase Rate",
        labels={
            "ViewCategory": "Number of Products Viewed",
            "PurchaseRate": "Purchase Rate (%)"
        },
        text=view_analysis["UserCount"].apply(lambda x: f"{x} users"),
        category_orders={"ViewCategory": category_order}
    )
    
    fig.update_layout(height=300)
    fig.update_traces(textposition='outside')
    
    return fig


def generate_behavior_insights(df):
    """
    Generates insights based on user behavior analysis.
    
    Parameters:
    df (pandas.DataFrame): The dataframe with user behavior data
    
    Returns:
    str: A string containing key insights
    """
    # Count users with different behaviors
    user_behaviors = {}
    for behavior in ["pv", "cart", "fav", "buy"]:
        user_behaviors[behavior] = df[df["BehaviorType"] == behavior]["UserID"].nunique()
    
    # Calculate conversion rates
    view_to_cart = (user_behaviors["cart"] / user_behaviors["pv"] * 100) if user_behaviors["pv"] > 0 else 0
    cart_to_buy = (user_behaviors["buy"] / user_behaviors["cart"] * 100) if user_behaviors["cart"] > 0 else 0
    
    # Analyze product view patterns
    user_product_views = df[df["BehaviorType"] == "pv"].groupby("UserID")["ItemID"].nunique().reset_index()
    user_product_views.columns = ["UserID", "ProductsViewed"]
    
    # Get users who purchased
    users_who_purchased = df[df["BehaviorType"] == "buy"]["UserID"].unique()
    
    # Add purchase flag to user_product_views
    user_product_views["Purchased"] = user_product_views["UserID"].isin(users_who_purchased)
    
    # Define high and low browsing thresholds
    user_product_views["HighBrowsing"] = user_product_views["ProductsViewed"] > 5
    
    # Calculate purchase rates for heavy vs light browsers
    heavy_browsers = user_product_views[user_product_views["HighBrowsing"]]
    light_browsers = user_product_views[~user_product_views["HighBrowsing"]]
    
    heavy_purchase_rate = heavy_browsers["Purchased"].mean() if not heavy_browsers.empty else 0
    light_purchase_rate = light_browsers["Purchased"].mean() if not light_browsers.empty else 0
    
    # Calculate purchase likelihood multiplier (avoid division by zero)
    purchase_likelihood_mult = (
        heavy_purchase_rate / light_purchase_rate if light_purchase_rate > 0 and not np.isnan(light_purchase_rate) else 0
    )
    
    # Generate the insights text
    insights = []
    
    # Only add insights with meaningful data
    if purchase_likelihood_mult > 1.2 and not np.isnan(purchase_likelihood_mult):
        insights.append(f"Users who browse more than 5 products are {purchase_likelihood_mult:.1f}x more likely to purchase.")
    
    if cart_to_buy > 0:
        insights.append(f"Our cart-to-purchase conversion rate is {cart_to_buy:.1f}%.")
    
    if user_behaviors["fav"] > 0 and user_behaviors["buy"] > 0:
        fav_to_buy = (user_behaviors["buy"] / user_behaviors["fav"] * 100)
        if fav_to_buy > 0:
            insights.append(f"Users who favorite items have a {fav_to_buy:.1f}% chance of making a purchase.")
    
    # Default insight if none of the above apply
    if not insights:
        insights.append("Analyze user behavior patterns to identify opportunities for improving the conversion funnel.")
    
    return " ".join(insights)