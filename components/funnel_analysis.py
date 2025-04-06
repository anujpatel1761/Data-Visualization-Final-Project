import pandas as pd
import plotly.express as px
import streamlit as st

def render_funnel_tab(df):
    st.markdown('<div class="section-header">Conversion Funnel</div>', unsafe_allow_html=True)

    # Compute dynamic funnel counts
    funnel_counts = df["BehaviorType"].value_counts()
    total_pv = funnel_counts.get("pv", 0)
    total_cart = funnel_counts.get("cart", 0)
    total_fav = funnel_counts.get("fav", 0)
    total_buy = funnel_counts.get("buy", 0)

    # Conversion rates
    cart_rate = (total_cart / total_pv) * 100 if total_pv > 0 else 0
    fav_rate = (total_fav / total_pv) * 100 if total_pv > 0 else 0
    buy_rate = (total_buy / total_pv) * 100 if total_pv > 0 else 0

    # Metric cards
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div style="font-size: 1rem; color: #7f8c8d; margin-bottom: 0.5rem;">Page Views</div>
            <div style="font-size: 1.5rem; font-weight: bold; color: #2c3e50;">{total_pv / 1e6:.2f}M</div>
            <div style="font-size: 0.9rem; color: #7f8c8d;">100%</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div style="font-size: 1rem; color: #7f8c8d; margin-bottom: 0.5rem;">Add to Cart</div>
            <div style="font-size: 1.5rem; font-weight: bold; color: #2c3e50;">{total_cart / 1e6:.2f}M</div>
            <div style="font-size: 0.9rem; color: #27ae60;">{cart_rate:.1f}%</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div style="font-size: 1rem; color: #7f8c8d; margin-bottom: 0.5rem;">Favorites</div>
            <div style="font-size: 1.5rem; font-weight: bold; color: #2c3e8;">{total_fav / 1e6:.2f}M</div>
            <div style="font-size: 0.9rem; color: #27ae60;">{fav_rate:.1f}%</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div style="font-size: 1rem; color: #7f8c8d; margin-bottom: 0.5rem;">Purchases</div>
            <div style="font-size: 1.5rem; font-weight: bold; color: #2c3e8;">{total_buy / 1e6:.2f}M</div>
            <div style="font-size: 0.9rem; color: #27ae60;">{buy_rate:.1f}%</div>
        </div>
        """, unsafe_allow_html=True)

    # Plot funnel chart
    funnel_df = pd.DataFrame({
        "Stage": ["Page View", "Add to Cart", "Favorite", "Purchase"],
        "Count": [total_pv, total_cart, total_fav, total_buy]
    })

    fig = px.funnel(funnel_df, x="Count", y="Stage", title="Full Conversion Funnel")
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)

    # 🔥 Real Heatmap: Funnel by Category
    st.markdown('<div class="section-header">Funnel by Category</div>', unsafe_allow_html=True)
    fig_heatmap = plot_category_conversion_heatmap(df)
    st.plotly_chart(fig_heatmap, use_container_width=True)

    # Insights
    st.markdown("""
    <div class="insight-box">
        <div style="font-weight: bold; margin-bottom: 0.5rem;">Funnel Insights:</div>
        <p>The biggest drop-off (typically ~70%) occurs between Page Views and Add to Cart, suggesting that product pages may need optimization. Electronics often leads in view-to-cart conversions, while Clothing converts carts to purchases more efficiently.</p>
    </div>
    """, unsafe_allow_html=True)


def plot_category_conversion_heatmap(df, top_n=10):
    # Count behavior per category
    behavior_pivot = df.pivot_table(
        index='CategoryID',
        columns='BehaviorType',
        values='UserID',
        aggfunc='count',
        fill_value=0
    ).reset_index()

    # Calculate conversion rates
    behavior_pivot['view_to_cart'] = (behavior_pivot['cart'] / behavior_pivot['pv']) * 100
    behavior_pivot['cart_to_buy'] = (behavior_pivot['buy'] / behavior_pivot['cart']) * 100

    # Limit to top N categories by views
    top_categories = behavior_pivot.sort_values(by='pv', ascending=False).head(top_n)

    # Melt for heatmap format
    heatmap_df = top_categories.melt(
        id_vars='CategoryID',
        value_vars=['view_to_cart', 'cart_to_buy'],
        var_name='Conversion Stage',
        value_name='Conversion Rate'
    )

    # Plot heatmap
    fig = px.density_heatmap(
        heatmap_df,
        x='Conversion Stage',
        y='CategoryID',
        z='Conversion Rate',
        color_continuous_scale='Blues',
        title="Conversion Rates by Category"
    )
    fig.update_layout(height=400, xaxis_title='', yaxis_title='Category ID')
    return fig
