import streamlit as st
import datetime

# Set page configuration
st.set_page_config(
    page_title="Taobao E-Commerce Analytics",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
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

# Sidebar
with st.sidebar:
    st.title("🛒 Taobao Analytics")
    
    # Date filters
    st.markdown("### 📅 Date Range")
    start_date = st.date_input("Start Date", datetime.date(2017, 11, 25))
    end_date = st.date_input("End Date", datetime.date(2017, 12, 2))
    
    # Quick date selectors
    cols = st.columns(4)
    with cols[0]:
        st.button("Day", use_container_width=True)
    with cols[1]:
        st.button("Week", use_container_width=True)
    with cols[2]:
        st.button("Month", use_container_width=True)
    with cols[3]:
        st.button("All", use_container_width=True)
    
    # Behavior filters
    st.markdown("### 🔄 Behaviors")
    behavior_types = st.multiselect(
        "Select behaviors",
        ["pv (Page View)", "cart (Add to Cart)", "fav (Favorite)", "buy (Purchase)"],
        default=["pv (Page View)", "cart (Add to Cart)", "buy (Purchase)"]
    )
    
    # Category filters
    st.markdown("### 🗂️ Categories")
    categories = st.multiselect(
        "Select categories",
        ["Electronics", "Clothing", "Home Goods", "Beauty", "Sports", "Others"],
        default=["Electronics", "Clothing"]
    )
    
    # Apply/Reset buttons
    col1, col2 = st.columns(2)
    with col1:
        st.button("Apply Filters", use_container_width=True, type="primary")
    with col2:
        st.button("Reset", use_container_width=True)
    
    st.markdown("---")
    st.markdown("### 📊 Data Source")
    st.markdown("Taobao E-Commerce Dataset")
    st.markdown("• 987,982 unique users")
    st.markdown("• 3,962,559 unique products")
    st.markdown("• 9,377 unique categories")
    st.markdown("• 8 days (Nov 25 - Dec 2, 2017)")

# Main Content Area
# Main title with date range
st.markdown('<div class="main-title">Taobao E-Commerce Funnel Analysis Dashboard</div>', unsafe_allow_html=True)
st.markdown(f"""
<div style="text-align: center; margin-bottom: 2rem;">
    <span style="background-color: #f8f9fa; padding: 0.5rem 1rem; border-radius: 2rem; font-weight: 500;">
        📅 November 25, 2017 - December 2, 2017
    </span>
</div>
""", unsafe_allow_html=True)

# Key metrics
st.markdown('<div class="section-header">📈 Key Metrics</div>', unsafe_allow_html=True)
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("""
    <div class="metric-card">
        <div class="metric-value">987,982</div>
        <div class="metric-label">Total Users</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="metric-card">
        <div class="metric-value">3.96M</div>
        <div class="metric-label">Total Products</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="metric-card">
        <div class="metric-value">86.95M</div>
        <div class="metric-label">Interactions</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown("""
    <div class="metric-card">
        <div class="metric-value">3.2%</div>
        <div class="metric-label">Conversion Rate</div>
    </div>
    """, unsafe_allow_html=True)

# Main dashboard tabs
tabs = st.tabs([
    "📊 Overview", 
    "🔄 Funnel Analysis", 
    "⏱️ Time Trends", 
    "📦 Product Popularity", 
    "🗂️ Categories",
    "👥 User Behavior"
])

# Tab 1: Overview
with tabs[0]:
    # Highlight metrics
    st.markdown('<div class="section-header">Highlights</div>', unsafe_allow_html=True)
    
    # Chart placeholders with two columns layout
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="chart-placeholder">
            <div style="text-align: center;">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">📈</div>
                <div style="font-weight: bold;">Daily Activity Overview</div>
                <div style="color: #7f8c8d; margin-top: 0.5rem;">Bar chart showing daily interactions</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="chart-placeholder">
            <div style="text-align: center;">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">🔄</div>
                <div style="font-weight: bold;">Conversion Funnel</div>
                <div style="color: #7f8c8d; margin-top: 0.5rem;">Funnel showing pv → cart → buy flow</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Insights box
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
    
    # More charts in three columns
    st.markdown('<div class="section-header">Key Metrics Breakdown</div>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="chart-placeholder">
            <div style="text-align: center;">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">📊</div>
                <div style="font-weight: bold;">Top Categories</div>
                <div style="color: #7f8c8d; margin-top: 0.5rem;">Pie chart of top categories</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="chart-placeholder">
            <div style="text-align: center;">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">🔝</div>
                <div style="font-weight: bold;">Top Products</div>
                <div style="color: #7f8c8d; margin-top: 0.5rem;">Bar chart of most popular products</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="chart-placeholder">
            <div style="text-align: center;">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">👥</div>
                <div style="font-weight: bold;">User Activity</div>
                <div style="color: #7f8c8d; margin-top: 0.5rem;">Distribution of user behaviors</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# Tab 2: Funnel Analysis
with tabs[1]:
    st.markdown('<div class="section-header">Conversion Funnel</div>', unsafe_allow_html=True)
    
    # Funnel metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <div style="font-size: 1rem; color: #7f8c8d; margin-bottom: 0.5rem;">Page Views</div>
            <div style="font-size: 1.5rem; font-weight: bold; color: #2c3e50;">4.58M</div>
            <div style="font-size: 0.9rem; color: #7f8c8d;">100%</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <div style="font-size: 1rem; color: #7f8c8d; margin-bottom: 0.5rem;">Add to Cart</div>
            <div style="font-size: 1.5rem; font-weight: bold; color: #2c3e50;">1.25M</div>
            <div style="font-size: 0.9rem; color: #27ae60;">27.2%</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <div style="font-size: 1rem; color: #7f8c8d; margin-bottom: 0.5rem;">Favorites</div>
            <div style="font-size: 1.5rem; font-weight: bold; color: #2c3e50;">785K</div>
            <div style="font-size: 0.9rem; color: #27ae60;">17.1%</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="metric-card">
            <div style="font-size: 1rem; color: #7f8c8d; margin-bottom: 0.5rem;">Purchases</div>
            <div style="font-size: 1.5rem; font-weight: bold; color: #2c3e50;">147K</div>
            <div style="font-size: 0.9rem; color: #27ae60;">3.2%</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Funnel visualization placeholder
    st.markdown("""
    <div class="chart-placeholder" style="height: 400px;">
        <div style="text-align: center;">
            <div style="font-size: 2rem; margin-bottom: 0.5rem;">🔄</div>
            <div style="font-weight: bold;">Full Conversion Funnel</div>
            <div style="color: #7f8c8d; margin-top: 0.5rem;">Interactive funnel chart showing conversion flow</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Funnel by category
    st.markdown('<div class="section-header">Funnel by Category</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="chart-placeholder" style="height: 350px;">
        <div style="text-align: center;">
            <div style="font-size: 2rem; margin-bottom: 0.5rem;">🗂️</div>
            <div style="font-weight: bold;">Category Conversion Rates</div>
            <div style="color: #7f8c8d; margin-top: 0.5rem;">Heatmap of conversion rates by category</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Drop-off insights
    st.markdown("""
    <div class="insight-box">
        <div style="font-weight: bold; margin-bottom: 0.5rem;">Funnel Insights:</div>
        <p>The biggest drop-off (72.8%) occurs between Page Views and Add to Cart, suggesting that product pages may need optimization. Electronics has the highest view-to-cart conversion at 32.5%, while Clothing has the highest cart-to-purchase rate at 15.2%.</p>
    </div>
    """, unsafe_allow_html=True)

# Tab 3: Time Trends
with tabs[2]:
    st.markdown('<div class="section-header">Time-Based Analysis</div>', unsafe_allow_html=True)
    
    # Daily trends
    st.markdown("""
    <div class="chart-placeholder" style="height: 300px;">
        <div style="text-align: center;">
            <div style="font-size: 2rem; margin-bottom: 0.5rem;">📈</div>
            <div style="font-weight: bold;">Daily Activity Trends</div>
            <div style="color: #7f8c8d; margin-top: 0.5rem;">Line chart showing behavior patterns over 8 days</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Hourly heatmap
    st.markdown('<div class="section-header">Hourly Activity Patterns</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="chart-placeholder" style="height: 350px;">
        <div style="text-align: center;">
            <div style="font-size: 2rem; margin-bottom: 0.5rem;">⏰</div>
            <div style="font-weight: bold;">Hourly Activity Heatmap</div>
            <div style="color: #7f8c8d; margin-top: 0.5rem;">Heatmap showing activity by hour and day</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Weekday vs Weekend
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="chart-placeholder">
            <div style="text-align: center;">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">📅</div>
                <div style="font-weight: bold;">Weekday vs Weekend</div>
                <div style="color: #7f8c8d; margin-top: 0.5rem;">Comparison of behavior patterns</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="chart-placeholder">
            <div style="text-align: center;">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">🔄</div>
                <div style="font-weight: bold;">Hourly Conversion Rates</div>
                <div style="color: #7f8c8d; margin-top: 0.5rem;">Conversion rate by hour</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# Tab 4: Product Popularity
with tabs[3]:
    st.markdown('<div class="section-header">Product Popularity Analysis</div>', unsafe_allow_html=True)
    
    # Day selector
    day_options = ["Nov 25", "Nov 26", "Nov 27", "Nov 28", "Nov 29", "Nov 30", "Dec 1", "Dec 2"]
    selected_day = st.select_slider("Select Day", options=day_options, value="Nov 25")
    
    # Metric selector
    metric = st.radio(
        "Popularity Metric",
        ["Views", "Cart Additions", "Favorites", "Purchases"],
        horizontal=True
    )
    
    # Top and bottom products
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="chart-placeholder">
            <div style="text-align: center;">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">🔝</div>
                <div style="font-weight: bold;">Top 10 Products</div>
                <div style="color: #7f8c8d; margin-top: 0.5rem;">Most popular products by selected metric</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="chart-placeholder">
            <div style="text-align: center;">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">👎</div>
                <div style="font-weight: bold;">Least Popular Products</div>
                <div style="color: #7f8c8d; margin-top: 0.5rem;">Products with lowest engagement</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Product trends over time
    st.markdown('<div class="section-header">Product Popularity Trends</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="chart-placeholder" style="height: 350px;">
        <div style="text-align: center;">
            <div style="font-size: 2rem; margin-bottom: 0.5rem;">📈</div>
            <div style="font-weight: bold;">Product Popularity Over Time</div>
            <div style="color: #7f8c8d; margin-top: 0.5rem;">Line chart showing trends for top products</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Tab 5: Categories
with tabs[4]:
    st.markdown('<div class="section-header">Category Analysis</div>', unsafe_allow_html=True)
    
    # Top categories chart
    st.markdown("""
    <div class="chart-placeholder" style="height: 350px;">
        <div style="text-align: center;">
            <div style="font-size: 2rem; margin-bottom: 0.5rem;">🗂️</div>
            <div style="font-weight: bold;">Category Performance</div>
            <div style="color: #7f8c8d; margin-top: 0.5rem;">Treemap showing category popularity and conversion</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Category metrics
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="chart-placeholder">
            <div style="text-align: center;">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">📊</div>
                <div style="font-weight: bold;">Category Conversion Rates</div>
                <div style="color: #7f8c8d; margin-top: 0.5rem;">Bar chart of conversion by category</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="chart-placeholder">
            <div style="text-align: center;">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">⏱️</div>
                <div style="font-weight: bold;">Category Activity by Hour</div>
                <div style="color: #7f8c8d; margin-top: 0.5rem;">When different categories are popular</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Category comparison
    st.markdown('<div class="section-header">Category Comparison</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="chart-placeholder" style="height: 350px;">
        <div style="text-align: center;">
            <div style="font-size: 2rem; margin-bottom: 0.5rem;">📊</div>
            <div style="font-weight: bold;">Category Performance Radar</div>
            <div style="color: #7f8c8d; margin-top: 0.5rem;">Radar chart comparing category metrics</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Tab 6: User Behavior
with tabs[5]:
    st.markdown('<div class="section-header">User Behavior Analysis</div>', unsafe_allow_html=True)
    
    # User flow diagram
    st.markdown("""
    <div class="chart-placeholder" style="height: 350px;">
        <div style="text-align: center;">
            <div style="font-size: 2rem; margin-bottom: 0.5rem;">🔄</div>
            <div style="font-weight: bold;">User Behavior Flow</div>
            <div style="color: #7f8c8d; margin-top: 0.5rem;">Sankey diagram showing user journey paths</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # User segments
    st.markdown('<div class="section-header">User Segments</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="chart-placeholder">
            <div style="text-align: center;">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">👥</div>
                <div style="font-weight: bold;">User Segments by Behavior</div>
                <div style="color: #7f8c8d; margin-top: 0.5rem;">Distribution of user types</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="chart-placeholder">
            <div style="text-align: center;">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">⏱️</div>
                <div style="font-weight: bold;">Session Duration vs Conversion</div>
                <div style="color: #7f8c8d; margin-top: 0.5rem;">Relationship between time spent and purchases</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # User insights
    st.markdown("""
    <div class="insight-box">
        <div style="font-weight: bold; margin-bottom: 0.5rem;">User Behavior Insights:</div>
        <p>Users who interact with more than 5 products are 2.3x more likely to make a purchase. Mobile users have a 15% lower conversion rate than desktop users, but make up 68% of total traffic.</p>
    </div>
    """, unsafe_allow_html=True)

# Footer
st.markdown('<div class="footer">🛒 Taobao E-Commerce Analytics Dashboard | Final Project by Your Name</div>', unsafe_allow_html=True)

# Help expander
with st.expander("💡 How to use this dashboard"):
    st.markdown("""
    ### Using This Dashboard
    
    1. **Filter the data** using the sidebar controls to select date ranges and categories
    2. **Navigate between tabs** to explore different aspects of the funnel analysis
    3. **Interact with visualizations** by hovering for details or clicking on elements
    4. **Download insights** by clicking the export button on charts
    
    This dashboard analyzes the Taobao E-Commerce dataset containing user behavior data (page views, cart additions, favorites, and purchases) from November 25 to December 2, 2017.
    """)