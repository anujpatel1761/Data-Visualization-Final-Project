import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime

def render_user_behavior_tab(df):
    """
    Renders the User Behavior tab with improved visualizations for user journeys,
    user segments, and session analysis.
    
    Parameters:
    df (pandas.DataFrame): The dataframe with e-commerce data
    """
    #st.markdown('<div class="section-header">User Behavior Analysis</div>', unsafe_allow_html=True)
    
    # Create a working copy of the dataframe
    df_work = df.copy()
    
    # Clean timestamps if needed
    if pd.api.types.is_object_dtype(df_work["Timestamp"]):
        df_work["Timestamp"] = df_work["Timestamp"].astype(str).str.extract(r'(\d{4}-\d{2}-\d{2}.+)')
        df_work["Timestamp"] = pd.to_datetime(df_work["Timestamp"], errors='coerce')
    
    # Create Sankey diagram data for user journeys
    # Create Sankey diagram data for user journeys
    user_journeys = create_user_journey_sankey(df_work)

    if user_journeys:
        #st.markdown('<div class="section-header">User Behavior Analysis</div>', unsafe_allow_html=True)
        st.plotly_chart(user_journeys, use_container_width=True)

        # Explanatory text
        st.markdown("""
        <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin-bottom: 20px;">
            <p><strong>How to Read This Chart:</strong> This Sankey diagram shows how users move through the purchase funnel. 
            The width of each flow represents the number of users taking that path. Thicker lines indicate more common user journeys.</p>
            <ul>
                <li><strong>Page View → Add to Cart:</strong> Users who viewed a product and then added it to their cart</li>
                <li><strong>Add to Cart → Purchase:</strong> Users who proceeded from cart to completing a purchase</li>
                <li><strong>Page View → Favorite:</strong> Users who viewed a product and saved it to favorites</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    # Else, do nothing (don't render the header or chart placeholder)



    # User segments section
    st.markdown('<div class="section-header">User Segments</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # User segments by behavior
        user_segments = create_user_segments_chart(df_work)
        if user_segments:
            st.plotly_chart(user_segments, use_container_width=True)
            
            # Add explanatory text for the pie chart
            st.markdown("""
            <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin-bottom: 20px;">
                <p><strong>User Segment Definitions:</strong></p>
                <ul>
                    <li><strong>Browsers:</strong> Users who only viewed products without adding to cart, favoriting, or purchasing</li>
                    <li><strong>Cart Abandoners:</strong> Users who added items to cart but did not complete a purchase</li>
                    <li><strong>Wishlisters:</strong> Users who favorited items but did not purchase</li>
                    <li><strong>Purchasers:</strong> Users who completed at least one purchase</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
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
            
            # Add explanatory text for the bar chart
            st.markdown("""
            <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin-bottom: 20px;">
                <p><strong>Purchase Probability:</strong> This chart shows how the likelihood of purchase changes based on how many products a user views. 
                The percentages represent conversion rates, while the text above each bar shows the number of users in each category.</p>
                <p><em>Key Insight: Users who view multiple products are generally more likely to make a purchase, suggesting that encouraging product exploration may increase conversion rates.</em></p>
            </div>
            """, unsafe_allow_html=True)
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
    
    # # Add action items for marketing and product teams
    # st.markdown("""
    # <div style="background-color: #eaf4fb; padding: 20px; border-radius: 5px; margin-top: 20px; border-left: 5px solid #3498db;">
    #     <h4 style="margin-top: 0; color: #2c3e50;">💡 Key Insights & Recommendations</h4>
    #     <p>{}</p>
    #     <h5 style="margin-top: 15px; color: #2c3e50;">Recommended Actions:</h5>
    #     <ul>
    #         <li><strong>For Cart Abandoners:</strong> Implement abandoned cart email reminders with incentives (e.g., free shipping, limited-time discounts)</li>
    #         <li><strong>For Browsers:</strong> Add product recommendation carousels to encourage more exploration</li>
    #         <li><strong>For Wishlisters:</strong> Send notifications for price drops on favorited items</li>
    #         <li><strong>For Purchasers:</strong> Create personalized follow-up campaigns based on purchase history</li>
    #     </ul>
    # </div>
    # """.format(insights), unsafe_allow_html=True)


def create_user_journey_sankey(df):
    """
    Creates an improved Sankey diagram showing user journey paths through the sales funnel.
    
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
    behavior_labels = {
        "pv": "Page View", 
        "cart": "Add to Cart", 
        "fav": "Favorite", 
        "buy": "Purchase"
    }
    
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
    
    # Define node colors with better visibility
    node_colors = [
        "#36A2EB",  # Blue for Page View
        "#FFCE56",  # Yellow for Add to Cart
        "#4BC0C0",  # Teal for Favorite
        "#FF6384"   # Pink for Purchase
    ]
    
    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=15,
            thickness=20,
            line=dict(color="black", width=0.5),
            label=node_labels,
            color=node_colors
        ),
        link=dict(
            source=sources,
            target=targets,
            value=values,
            # Use semi-transparent colors based on target node
            color=[f"rgba({','.join(str(int(c * 255)) for c in px.colors.hex_to_rgb(node_colors[t]))}, 0.4)" for s, t in zip(sources, targets)]
        )
    )])
    
    # fig.update_layout(
    #     title={
    #         'text': "User Journey Flow: How Users Navigate Through the Site",
    #         'y': 0.95,
    #         'x': 0.5,
    #         'xanchor': 'center',
    #         'yanchor': 'top'
    #     },
    #     height=400,
    #     font=dict(size=12),
    #     margin=dict(l=0, r=0, t=40, b=0)
    # )
    
    # return fig


def create_user_segments_chart(df):
    """
    Creates an improved chart showing user segments based on their behavior patterns.
    
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
    
    # Improve segment labels with counts and percentages
    segment_df["SegmentLabel"] = segment_df.apply(
        lambda row: f"{row['Segment']}<br>{row['Users']:,} users<br>({row['Percentage']:.1f}%)", 
        axis=1
    )
    
    # Choose more intuitive colors
    color_map = {
        "Browsers": "#36A2EB",       # Blue
        "Cart Abandoners": "#FFCE56", # Yellow
        "Wishlisters": "#4BC0C0",     # Teal
        "Purchasers": "#FF6384"       # Pink
    }
    
    # Create a donut chart instead of a pie chart
    fig = px.pie(
        segment_df,
        names="Segment",
        values="Users",
        title="User Segments by Behavior Type",
        color="Segment",
        color_discrete_map=color_map,
        hover_data=["Users", "Percentage"],
        hole=0.4,  # Create a donut chart
        custom_data=["SegmentLabel"]
    )
    
    # Improve text positioning and information
    fig.update_traces(
        textposition='inside',
        textinfo='percent',
        hovertemplate='<b>%{label}</b><br>Users: %{value:,}<br>Percentage: %{percent}<extra></extra>',
        textfont_size=12,
        insidetextorientation='horizontal'
    )
    
    # Add a descriptive annotation in the center
    fig.add_annotation(
        x=0.5, y=0.5,
        text=f"Total<br>{total_users:,}<br>Users",
        showarrow=False,
        font=dict(size=12)
    )
    
    fig.update_layout(
        height=350,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.1,
            xanchor="center",
            x=0.5
        ),
        margin=dict(l=20, r=20, t=50, b=20)
    )
    
    return fig


def create_session_analysis_chart(df):
    """
    Creates an improved chart showing the relationship between products viewed and purchase probability.
    
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
    
    # Create product view bins
    user_product_views["ViewCategory"] = pd.cut(
        user_product_views["ProductsViewed"],
        bins=[0, 1, 2, 5, 10, float('inf')],
        labels=["1 product", "2 products", "3-5 products", "6-10 products", "11+ products"],
        right=True
    )
    
    # Define the order of categories for plotting
    category_order = ["1 product", "2 products", "3-5 products", "6-10 products", "11+ products"]
    
    # Calculate purchase rate by view category
    purchase_rate = user_product_views.groupby("ViewCategory")["Purchased"].agg(
        ["mean", "count"]
    ).reset_index()
    purchase_rate["PurchaseRate"] = purchase_rate["mean"] * 100
    purchase_rate["UserCount"] = purchase_rate["count"]
    
    # Create a more descriptive chart with gradient color based on purchase rate
    fig = px.bar(
        purchase_rate,
        x="ViewCategory",
        y="PurchaseRate",
        color="PurchaseRate",
        text="UserCount",
        labels={
            "ViewCategory": "Number of Products Viewed",
            "PurchaseRate": "Purchase Rate (%)",
            "UserCount": "Number of Users"
        },
        title="Purchase Probability by Product Exploration",
        category_orders={"ViewCategory": category_order},
        color_continuous_scale="Viridis"  # Green-to-purple gradient
    )
    
    # Add value labels directly on the bars
    fig.update_traces(
        texttemplate='%{y:.1f}%<br>(%{text:,} users)',
        textposition='outside',
        hovertemplate='<b>%{x}</b><br>Purchase Rate: %{y:.1f}%<br>Users: %{text:,}<extra></extra>'
    )
    
    # Add a trend line to emphasize the pattern
    x_values = list(range(len(purchase_rate)))
    y_values = purchase_rate["PurchaseRate"].tolist()
    
    fig.add_trace(go.Scatter(
        x=purchase_rate["ViewCategory"],
        y=purchase_rate["PurchaseRate"],
        mode='lines',
        line=dict(color='rgba(255, 0, 0, 0.7)', width=2, dash='dot'),
        name='Trend',
        hoverinfo='skip'
    ))
    
    fig.update_layout(
        height=350,
        xaxis=dict(title="Number of Products Viewed"),
        yaxis=dict(
            title="Purchase Rate (%)",
            range=[0, max(purchase_rate["PurchaseRate"]) * 1.2]  # Add 20% padding
        ),
        coloraxis_showscale=False,  # Hide the color scale
        showlegend=False,
        margin=dict(l=20, r=20, t=50, b=20)
    )
    
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
    
    # Generate more structured and actionable insights
    insights = []
    
    # Only add insights with meaningful data
    if purchase_likelihood_mult > 1.2 and not np.isnan(purchase_likelihood_mult):
        insights.append(f"Users who browse more than 5 products are <b>{purchase_likelihood_mult:.1f}x more likely to purchase</b>, suggesting that increasing product discovery could boost sales.")
    
    if view_to_cart > 0:
        insights.append(f"The view-to-cart conversion rate is <b>{view_to_cart:.1f}%</b>, with <b>{user_behaviors['cart']:,}</b> users adding items to cart from <b>{user_behaviors['pv']:,}</b> who viewed products.")
    
    if cart_to_buy > 0:
        insights.append(f"The cart-to-purchase conversion rate is <b>{cart_to_buy:.1f}%</b>, with <b>{user_behaviors['buy']:,}</b> users completing purchases from <b>{user_behaviors['cart']:,}</b> with items in cart.")
    
    if user_behaviors["fav"] > 0 and user_behaviors["buy"] > 0:
        fav_to_buy = (user_behaviors["buy"] / user_behaviors["fav"] * 100)
        if fav_to_buy > 0:
            insights.append(f"<b>{fav_to_buy:.1f}%</b> of users who favorite items eventually make a purchase, highlighting the importance of the wishlist feature in the purchasing journey.")
    
    # Calculate cart abandonment rate
    if user_behaviors["cart"] > 0:
        cart_abandonment = (1 - (user_behaviors["buy"] / user_behaviors["cart"])) * 100
        insights.append(f"The cart abandonment rate is <b>{cart_abandonment:.1f}%</b>, representing a significant opportunity for recovery campaigns.")
    
    # Default insight if none of the above apply
    if not insights:
        insights.append("Analyze user behavior patterns to identify opportunities for improving the conversion funnel.")
    
    return " ".join(insights)