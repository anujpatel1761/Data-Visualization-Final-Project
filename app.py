import streamlit as st
import pandas as pd
import datetime
import plotly.express as px

from components.sidebar_filters import render_sidebar

from components.overview import create_daily_activity_overview,create_conversion_funnel,plot_top_categories,plot_top_products,plot_behavior_distribution,render_overview_tab
from components.funnel_analysis import render_funnel_tab
from components.time_trends import render_time_trends_tab
from components.product_popularity import render_product_popularity_tab
from components.category_analysis import render_category_analysis_tab
from components.user_behavior import render_user_behavior_tab




# -----------------------------
# Caching Function to Load Data
# -----------------------------
# This function uses Streamlit's caching to load the data once and reuse it.
# -----------------------------
# Set page configuration
# -----------------------------
st.set_page_config(
    page_title="E-Commerce Data Analytics",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

@st.cache_data(show_spinner=True)
def load_data(parquet_file_path):
    df = pd.read_parquet(parquet_file_path)

    # Clean the Timestamp column by removing the ID prefix
    if pd.api.types.is_object_dtype(df["Timestamp"]):
        # Extract just the timestamp part (everything after the ID number)
        df["Timestamp"] = df["Timestamp"].astype(str).str.extract(r'(\d{4}-\d{2}-\d{2}.+)')
    
    # Convert Timestamp to datetime if necessary
    if not pd.api.types.is_datetime64_any_dtype(df["Timestamp"]):
        df["Timestamp"] = pd.to_datetime(df["Timestamp"], errors='coerce')

    return df

data_path = r"C:\Users\anujp\Desktop\Data-Visualization-Final-Project\data\UserBehavior\user_behavior_sample_1000000.parquet"
df = load_data(data_path)





# -----------------------------
# Custom CSS for better UI
# -----------------------------
st.markdown("""
<style>
    /* Main styling */
    .main-title {
        font-size: 2.5rem;
        font-weight: bold;
        color: #2c3e50;
        text-align: center;
        margin-bottom: 1.5rem;
        padding-bottom: 1rem;
        border-bottom: 2px solid #eaeaea;
    }
    
    /* Card styling */
    .metric-card {
        background-color: white;
        border-radius: 0.5rem;
        padding: 1.5rem;
        box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
        text-align: center;
        margin-bottom: 1rem;
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
        color: #2c3e50;
        margin-bottom: 0.5rem;
    }
    
    .metric-label {
        font-size: 1rem;
        color: #7f8c8d;
    }
    
    /* Section styling */
    .section-header {
        font-size: 1.5rem;
        font-weight: bold;
        color: #2c3e50;
        margin-top: 2rem;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 1px solid #eaeaea;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 4rem;
        white-space: pre-wrap;
        border-radius: 4px 4px 0px 0px;
        padding: 1rem 1.5rem;
        background-color: #f8f9fa;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #e6f7ff;
        border-bottom: 2px solid #1890ff;
    }
    
    /* Chart placeholders */
    .chart-placeholder {
        background-color: #f8f9fa;
        border: 1px dashed #dee2e6;
        border-radius: 0.5rem;
        height: 300px;
        display: flex;
        justify-content: center;
        align-items: center;
        margin-bottom: 1rem;
    }
    
    /* Insight box */
    .insight-box {
        background-color: #e6f7ff;
        border-left: 4px solid #1890ff;
        padding: 1rem;
        margin-top: 1rem;
        margin-bottom: 1rem;
    }
    
    /* Footer */
    .footer {
        margin-top: 3rem;
        padding-top: 1rem;
        text-align: center;
        color: #7f8c8d;
        border-top: 1px solid #eaeaea;
    }
</style>
""", unsafe_allow_html=True)








# -----------------------------
# Sidebar: Filters and Data Source
# -----------------------------
df = render_sidebar(df, data_path, load_data)




# -----------------------------
# Main Content Area: Header and Key Metrics
# -----------------------------
st.markdown('<div class="main-title">E-Commerce Funnel Analysis Dashboard</div>', unsafe_allow_html=True)
st.markdown(f"""
<div style="text-align: center; margin-bottom: 2rem;">
    <span style="background-color: #f8f9fa; padding: 0.5rem 1rem; border-radius: 2rem; font-weight: 500;">
        📅 {st.session_state.start_date.strftime('%b %d, %Y')} - {st.session_state.end_date.strftime('%b %d, %Y')}
    </span>
</div>
""", unsafe_allow_html=True)



# -----------------------------
# Key Metrics (Consider calculating these from df for dynamic updates)
# -----------------------------
st.markdown('<div class="section-header">📈 Key Metrics</div>', unsafe_allow_html=True)
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{df["UserID"].nunique():,}</div>
        <div class="metric-label">Total Users</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{df["ItemID"].nunique()/1e6:.2f}M</div>
        <div class="metric-label">Total Products</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{df.shape[0]/1e6:.2f}M</div>
        <div class="metric-label">Interactions</div>
    </div>
    """, unsafe_allow_html=True)
with col4:
    # Count page views and purchases
    pv_count = df[df['BehaviorType'] == 'pv'].shape[0]
    buy_count = df[df['BehaviorType'] == 'buy'].shape[0]
    
    # Calculate conversion rate (handle division by zero)
    if pv_count > 0:
        conversion_rate = (buy_count / pv_count) * 100
    else:
        conversion_rate = 0
    
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{conversion_rate:.1f}%</div>
        <div class="metric-label">Conversion Rate</div>
    </div>
    """, unsafe_allow_html=True)




# -----------------------------
# Main Dashboard Tabs
# -----------------------------
tabs = st.tabs([
    "📊 Overview", 
    "🔄 Funnel Analysis", 
    "⏱️ Time Trends", 
    "📦 Product Popularity", 
    "🗂️ Categories",
    "👥 User Behavior"
])




# -----------------------------
# Tab 1: Overview - Dynamic Plotly Charts for Daily Activity Overview
# -----------------------------
with tabs[0]:
    render_overview_tab(df)
    
# -----------------------------
# Tab 2: Funnel Analysis - Enhanced with Dynamic Plotly Charts
# -----------------------------
with tabs[1]:
    render_funnel_tab(df)

# -----------------------------
# Tab 3: Time Trends - Dynamic Plotly Charts for Time-Based Analysis
# -----------------------------
with tabs[2]:
    render_time_trends_tab(df)

# -----------------------------
# Tab 4: Product Popularity - Interactive Controls Added
# -----------------------------
with tabs[3]:  # Make sure this matches the order of your tabs
    render_product_popularity_tab(df)

# -----------------------------
# Tab 5: Categories - Dynamic Category Analysis
# -----------------------------
with tabs[4]:
    render_category_analysis_tab(df)

# -----------------------------
# Tab 6: User Behavior - Dynamic Visualizations
# -----------------------------
with tabs[5]:
    render_user_behavior_tab(df)





# -----------------------------
# Footer and Help Section
# -----------------------------

# Footer with project information
st.markdown("""
<div class="footer">
    <div style="display: flex; justify-content: space-between; align-items: center; padding: 1rem 0;">
        <div>
            🛒 <span style="font-weight: 500;">E-Commerce Analytics Dashboard</span> 
            | Final Project by Anuj Patel & Jaimin Surathiy
        </div>
        <div>
            <span style="color: #6c757d; font-size: 0.9rem;">Data Visualization Course • Spring 2025</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Comprehensive help section
with st.expander("💡 How to use this dashboard"):
    col1, col2 = st.columns([3, 2])
    
    with col1:
        st.markdown("""
        ### Dashboard Guide
        
        This interactive dashboard provides comprehensive analysis of e-commerce user behavior data.
        
        #### Navigation Tips
        
        1. **Filter your data**: Use the sidebar controls to:
           - Select specific date ranges
           - Filter by user behavior types
           - Focus on specific product categories
        
        2. **Explore different perspectives**: Navigate between tabs to analyze:
           - Overview metrics and general trends
           - Detailed funnel conversion analysis
           - Time-based patterns in user behavior
           - Product popularity rankings
           - Category performance comparisons
           - User behavior patterns and segments
        
        3. **Interact with visualizations**:
           - Hover over charts for detailed tooltips
           - Click on legend items to filter data
           - Use the zoom and pan tools to explore dense charts
           - Download charts as PNG files using the camera icon
        
        #### Data Information
        
        The dataset contains user interaction logs from covering November 25 to December 2, 2017, with four types of user behaviors:
        - **Page View (pv)**: User viewed a product page
        - **Add to Cart (cart)**: User added product to shopping cart
        - **Favorite (fav)**: User saved product to favorites/wishlist
        - **Purchase (buy)**: User completed purchase of product
        """)
    
    with col2:
        # Quick reference for tabs
        st.markdown("""
        ### Tab Quick Reference
        
        **📊 Overview**
        Key metrics, daily activity, funnel summary
        
        **🔄 Funnel Analysis**
        Conversion rates, dropout points, category performance
        
        **⏱️ Time Trends**
        Hourly and daily patterns, weekday vs weekend
        
        **📦 Product Popularity**
        Top products, least popular items, popularity trends
        
        **🗂️ Categories**
        Category performance, conversion rates by category
        
        **👥 User Behavior**
        User journey flows, segments, purchase patterns
        """)
        
        # Simple visual tip
        st.image("https://via.placeholder.com/350x220", caption="Sample interaction: Try hovering and clicking on chart elements")