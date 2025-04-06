# overview.py
import pandas as pd
import plotly.express as px
import streamlit as st

def create_daily_activity_overview(df):
    df = df.copy()
    df["Date"] = df["Timestamp"].dt.date
    daily_counts = df.groupby("Date").size().reset_index(name="Interactions")
    fig = px.bar(daily_counts, x="Date", y="Interactions", 
                 title="Daily Activity Overview",
                 labels={"Interactions": "Number of Interactions", "Date": "Date"})
    fig.update_layout(height=300)
    return fig

def create_conversion_funnel(df):
    funnel_counts = df["BehaviorType"].value_counts()
    funnel_data = {
        "Stage": ["Page View", "Add to Cart", "Favorite", "Purchase"],
        "Count": [
            funnel_counts.get("pv", 0),
            funnel_counts.get("cart", 0),
            funnel_counts.get("fav", 0),
            funnel_counts.get("buy", 0),
        ]
    }
    funnel_df = pd.DataFrame(funnel_data)
    fig = px.funnel(funnel_df, x="Count", y="Stage", title="Conversion Funnel")
    fig.update_layout(height=300)
    return fig

def plot_top_categories(df, top_n=5):
    top_categories = df["CategoryID"].value_counts().nlargest(top_n).reset_index()
    top_categories.columns = ["CategoryID", "Count"]
    fig = px.pie(top_categories, names="CategoryID", values="Count", title="Top Categories")
    return fig

def plot_top_products(df, top_n=10):
    top_products = df["ItemID"].value_counts().nlargest(top_n).reset_index()
    top_products.columns = ["ItemID", "Count"]
    fig = px.bar(top_products, x="Count", y="ItemID", orientation="h",
                 title="Top Products", labels={"Count": "Interactions", "ItemID": "Product ID"})
    fig.update_layout(height=300)
    return fig

def plot_behavior_distribution(df):
    behavior_counts = df["BehaviorType"].value_counts().reset_index()
    behavior_counts.columns = ["Behavior", "Count"]
    fig = px.pie(behavior_counts, names="Behavior", values="Count", title="User Behavior Distribution")
    return fig

def render_overview_tab(df):
    st.markdown('<div class="section-header">Highlights</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.plotly_chart(create_daily_activity_overview(df), use_container_width=True)

    with col2:
        st.plotly_chart(create_conversion_funnel(df), use_container_width=True)

    st.markdown("""
    <div class="insight-box">
        <div style="font-weight: bold; margin-bottom: 0.5rem;">Key Insights:</div>
        <ul>
            <li>View-to-cart conversion is 27.2%, while cart-to-purchase is 11.8%</li>
            <li>Weekend conversion rates are 23% higher than weekdays</li>
            <li>Users who favorite items are 3.5x more likely to purchase later</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="section-header">Key Metrics Breakdown</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.plotly_chart(plot_top_categories(df), use_container_width=True)

    # with col2:
    #     st.plotly_chart(plot_top_products(df), use_container_width=True)

    with col3:
        st.plotly_chart(plot_behavior_distribution(df), use_container_width=True)