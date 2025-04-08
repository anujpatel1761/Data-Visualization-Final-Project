import streamlit as st
import pandas as pd
import datetime

# Mapping CategoryID to readable CategoryName
category_mapping = {
    4756105: 'Beauty',
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

def render_sidebar(df, data_path, load_data_func):
    with st.sidebar:
        st.title("🛒 SmartShopper Insights")

        if 'start_date' not in st.session_state:
            st.session_state.start_date = datetime.date(2017, 11, 25)
        if 'end_date' not in st.session_state:
            st.session_state.end_date = datetime.date(2017, 12, 2)

        st.markdown("### 📅 Date Range")
        start_date = st.date_input("Start Date", st.session_state.start_date)
        end_date = st.date_input("End Date", st.session_state.end_date)

        if start_date != st.session_state.start_date:
            st.session_state.start_date = start_date
        if end_date != st.session_state.end_date:
            st.session_state.end_date = end_date

        def set_day():
            st.session_state.start_date = st.session_state.end_date
            st.rerun()

        def set_week():
            st.session_state.start_date = st.session_state.end_date - datetime.timedelta(days=7)
            st.rerun()

        def set_month():
            st.session_state.start_date = st.session_state.end_date - datetime.timedelta(days=30)
            st.rerun()

        def set_all():
            st.session_state.start_date = datetime.date(2017, 11, 25)
            st.session_state.end_date = datetime.date(2017, 12, 2)
            st.rerun()

        cols = st.columns(4)
        with cols[0]:
            st.button("Day", use_container_width=True, on_click=set_day)
        with cols[1]:
            st.button("Week", use_container_width=True, on_click=set_week)
        with cols[2]:
            st.button("Month", use_container_width=True, on_click=set_month)
        with cols[3]:
            st.button("All", use_container_width=True, on_click=set_all)

        # Behavior filters
        st.markdown("### 🔄 Behaviors")
        behavior_map = {
            "pv (Page View)": "pv",
            "cart (Add to Cart)": "cart",
            "fav (Favorite)": "fav",
            "buy (Purchase)": "buy"
        }
        behavior_display_options = list(behavior_map.keys())
        selected_behavior_displays = st.multiselect(
            "Select behaviors",
            behavior_display_options,
            default=[]  # No default selection
        )
        selected_behaviors = [behavior_map[display] for display in selected_behavior_displays]

        # Map CategoryID to CategoryName
        df["CategoryName"] = df["CategoryID"].map(category_mapping).fillna("Other")

        st.markdown("### 🗂️ Categories")

        @st.cache_data(show_spinner=False)
        def get_top_category_names(df, n=6):
            top_ids = df["CategoryID"].value_counts().nlargest(n).index.tolist()
            return [category_mapping.get(cid, "Other") for cid in top_ids]

        top_category_names = get_top_category_names(df)

        selected_category_names = st.multiselect(
            "Select categories",
            top_category_names,
            default=[]  # No default selection
        )

        reverse_category_map = {v: k for k, v in category_mapping.items()}
        selected_category_ids = [
            reverse_category_map[name]
            for name in selected_category_names
            if name in reverse_category_map
        ]

        # Apply / Reset Buttons
        col1, col2 = st.columns(2)
        with col1:
            apply_filters_button = st.button("Apply Filters", use_container_width=True, key="apply")
        with col2:
            reset_filters_button = st.button("Reset", use_container_width=True, key="reset")

        @st.cache_data(show_spinner=False)
        def get_dataset_stats(parquet_file_path):
            df_stats = pd.read_parquet(parquet_file_path)
            if not pd.api.types.is_datetime64_any_dtype(df_stats["Timestamp"]):
                df_stats["Timestamp"] = pd.to_datetime(df_stats["Timestamp"], unit='s', origin='unix', errors='coerce')
            stats = {
                "users": df_stats["UserID"].nunique(),
                "products": df_stats["ItemID"].nunique(),
                "categories": df_stats["CategoryID"].nunique(),
                "start_date": df_stats["Timestamp"].min().date() if pd.notna(df_stats["Timestamp"].min()) else None,
                "end_date": df_stats["Timestamp"].max().date() if pd.notna(df_stats["Timestamp"].max()) else None,
                "days": ((df_stats["Timestamp"].max().date() - df_stats["Timestamp"].min().date()).days + 1)
                        if pd.notna(df_stats["Timestamp"].max()) and pd.notna(df_stats["Timestamp"].min()) else "Unknown"
            }
            return stats

        dataset_stats = get_dataset_stats(data_path)

        start_date_fmt = dataset_stats["start_date"].strftime('%b %d') if dataset_stats["start_date"] else "Unknown"
        end_date_fmt = dataset_stats["end_date"].strftime('%b %d, %Y') if dataset_stats["end_date"] else "Unknown"

        st.markdown("---")
        st.markdown("### 📊 Data Source")
        st.markdown("Taobao E-Commerce Dataset")
        st.markdown(f"• {dataset_stats['users']:,} unique users")
        st.markdown(f"• {dataset_stats['products']:,} unique products")
        st.markdown(f"• {dataset_stats['categories']:,} unique categories")
        st.markdown(f"• {dataset_stats['days']} days ({start_date_fmt} - {end_date_fmt})")

    # Filtering logic
    def apply_all_filters():
        if 'original_df' not in st.session_state:
            st.session_state.original_df = df.copy()

        filtered_df = st.session_state.original_df.copy()
        start_datetime = pd.Timestamp(start_date)
        end_datetime = pd.Timestamp(end_date)

        filtered_df = filtered_df[
            (filtered_df["Timestamp"] >= start_datetime) & 
            (filtered_df["Timestamp"] <= end_datetime + pd.Timedelta(days=1))
        ]

        if selected_behaviors:
            filtered_df = filtered_df[filtered_df["BehaviorType"].isin(selected_behaviors)]

        if selected_category_ids:
            filtered_df = filtered_df[filtered_df["CategoryID"].isin(selected_category_ids)]

        return filtered_df

    def reset_filters():
        if 'original_df' in st.session_state:
            return st.session_state.original_df.copy()
        else:
            return load_data_func(data_path)

    if apply_filters_button:
        filtered_df = apply_all_filters()
    elif reset_filters_button:
        filtered_df = reset_filters()
    else:
        filtered_df = df

    return filtered_df
