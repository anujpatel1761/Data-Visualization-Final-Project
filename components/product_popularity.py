import streamlit as st
import pandas as pd
import plotly.express as px

# --- Final Clean Product Name Mapping --- #
final_product_name_mapping = {
    812879: 'Gaming Laptop',
    138964: 'Graphics Card',
    3845720: 'MobilePhones',
    2331370: 'Cat Litter Box',
    2338453: "Men's T-Shirt",
    1535294: "Women's Jacket",
    2032668: 'Electric Guitar',
    4211339: 'Digital Piano',
    33711523: 'Baby Stroller',
    2367945: 'Infant Diapers',
    25203771: 'Garden Hose',
    25203772: 'Outdoor Planter',
    30102021: 'Mystery Novel',
    30102022: 'Python Programming Book',
    47852011: 'Vitamin C Tablets',
    47852012: 'Resistance Bands',
    68231001: 'LEGO Set',
    68231002: 'Action Figure',
    55519991: 'Electric Drill',
    55519992: 'Screwdriver Set',
    10000011: 'Car Vacuum Cleaner',
    10000012: 'Dashboard Camera',
    10000021: 'Wireless Earbuds',
    10000022: 'Smartphone',
    10000031: 'Office Chair',
    10000032: 'Coffee Table',
    10000041: 'Organic Almonds',
    10000042: 'Pasta Pack',
    10000051: 'Digital Sports Watch',
    10000052: 'Leather Strap Watch',
    10000061: 'Stapler',
    10000062: 'Notebook Set',
    10000071: 'Soccer Ball',
    10000072: 'Tennis Racket',
    10000081: 'Blender',
    10000082: 'Air Fryer',
    10000091: 'Running Shoes',
    10000092: 'Leather Boots',
    10000101: 'Gold Necklace',
    10000102: 'Diamond Ring'
}

# --- Helper to Fetch Product Name --- #
def get_product_name(item_id):
    return final_product_name_mapping.get(item_id, f"Product {item_id}")

# --- Streamlit Function --- #
def render_product_popularity_tab(df):
    st.markdown('<div class="section-header">Overall Product Popularity</div>', unsafe_allow_html=True)

    df_work = df.copy()

    # Clean Timestamp if necessary
    if pd.api.types.is_object_dtype(df_work["Timestamp"]):
        df_work["Timestamp"] = df_work["Timestamp"].astype(str).str.extract(r'(\d{4}-\d{2}-\d{2}.+)')
        df_work["Timestamp"] = pd.to_datetime(df_work["Timestamp"], errors='coerce')

    # ---------------- Top 10 Products ---------------- #
    top_counts = df_work["ItemID"].value_counts().head(10)
    top_products = pd.DataFrame({
        'item_id': top_counts.index,
        'count': top_counts.values
    })
    top_products['item_label'] = top_products['item_id'].apply(get_product_name)

    st.subheader("Top 10 Products (Overall)")
    if not top_products.empty:
        fig_top = px.bar(
            top_products, x="count", y="item_label", orientation="h",
            labels={"count": "Total Interactions", "item_label": "Product"}
        )
        fig_top.update_traces(marker_color="#3498db", marker_line_color="#2980b9", marker_line_width=1)
        fig_top.update_layout(height=450, yaxis=dict(autorange="reversed"))
        st.plotly_chart(fig_top, use_container_width=True)
    else:
        st.info("No data available for top products.")

   
