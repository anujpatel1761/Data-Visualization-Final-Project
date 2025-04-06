import streamlit as st
import pandas as pd
import datetime

def render_sidebar(df, data_path, load_data_func):
    """
    Renders the sidebar with filters and returns the filtered dataframe
    
    Parameters:
    df (pandas.DataFrame): The current dataframe
    data_path (str): Path to the original data file
    load_data_func (function): Function to load the data
    
    Returns:
    pandas.DataFrame: The filtered dataframe based on user selections
    """
    with st.sidebar:
        st.title("🛒 Taobao Analytics")
        
        # Use session state to persist filter selections
        if 'start_date' not in st.session_state:
            st.session_state.start_date = datetime.date(2017, 11, 25)
        if 'end_date' not in st.session_state:
            st.session_state.end_date = datetime.date(2017, 12, 2)
        
        # Date filters with session state values as defaults
        st.markdown("### 📅 Date Range")
        start_date = st.date_input("Start Date", st.session_state.start_date)
        end_date = st.date_input("End Date", st.session_state.end_date)
        
        # Update session state when date inputs change
        if start_date != st.session_state.start_date:
            st.session_state.start_date = start_date
        if end_date != st.session_state.end_date:
            st.session_state.end_date = end_date
        
        # Quick date selectors with callback functions
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
            if st.button("Day", use_container_width=True, on_click=set_day):
                pass
        with cols[1]:
            if st.button("Week", use_container_width=True, on_click=set_week):
                pass
        with cols[2]:
            if st.button("Month", use_container_width=True, on_click=set_month):
                pass
        with cols[3]:
            if st.button("All", use_container_width=True, on_click=set_all):
                pass
        
        # Map display names to actual behavior values in the dataset
        behavior_map = {
            "pv (Page View)": "pv",
            "cart (Add to Cart)": "cart",
            "fav (Favorite)": "fav",
            "buy (Purchase)": "buy"
        }
        
        # Behavior filters
        st.markdown("### 🔄 Behaviors")
        behavior_display_options = list(behavior_map.keys())
        selected_behavior_displays = st.multiselect(
            "Select behaviors",
            behavior_display_options,
            default=["pv (Page View)", "cart (Add to Cart)", "buy (Purchase)"]
        )
        
        # Convert selected display names to actual values
        selected_behaviors = [behavior_map[display] for display in selected_behavior_displays]
        
        # Category filters - displaying actual category IDs
        st.markdown("### 🗂️ Categories")
        # Get top category IDs
        @st.cache_data(show_spinner=False)
        def get_top_categories(df, n=6):
            return df["CategoryID"].value_counts().nlargest(n).index.tolist()
        
        top_category_ids = get_top_categories(df)
        selected_category_ids = st.multiselect(
            "Select category IDs",
            top_category_ids,
            default=top_category_ids[:2] if len(top_category_ids) >= 2 else top_category_ids
        )
        
        # Apply/Reset buttons
        col1, col2 = st.columns(2)
        
        with col1:
            apply_filters_button = st.button("Apply Filters", use_container_width=True, key="apply")
        with col2:
            reset_filters_button = st.button("Reset", use_container_width=True, key="reset")
        
        # Load the full dataset once for statistics (before any filtering)
        @st.cache_data(show_spinner=False)
        def get_dataset_stats(parquet_file_path):
            df_stats = pd.read_parquet(parquet_file_path)

            # Ensure Timestamp is in datetime format
            if not pd.api.types.is_datetime64_any_dtype(df_stats["Timestamp"]):
                df_stats["Timestamp"] = pd.to_datetime(df_stats["Timestamp"], unit='s', origin='unix', errors='coerce')

            # Now it's safe to use .date()
            stats = {
                "users": df_stats["UserID"].nunique(),
                "products": df_stats["ItemID"].nunique(),
                "categories": df_stats["CategoryID"].nunique(),
                "start_date": df_stats["Timestamp"].min().date(),
                "end_date": df_stats["Timestamp"].max().date(),
                "days": (df_stats["Timestamp"].max().date() - df_stats["Timestamp"].min().date()).days + 1
            }
            return stats

        # Get the statistics (this runs once and caches the result)
        dataset_stats = get_dataset_stats(data_path)

        # In your sidebar section:
        st.markdown("---")
        st.markdown("### 📊 Data Source")
        st.markdown("Taobao E-Commerce Dataset")
        st.markdown(f"• {dataset_stats['users']:,} unique users")
        st.markdown(f"• {dataset_stats['products']:,} unique products")
        st.markdown(f"• {dataset_stats['categories']:,} unique categories")

        # Use safe formatting
        start_date_fmt = dataset_stats["start_date"].strftime('%b %d') if pd.notna(dataset_stats["start_date"]) else "Unknown"
        end_date_fmt = dataset_stats["end_date"].strftime('%b %d, %Y') if pd.notna(dataset_stats["end_date"]) else "Unknown"

        # Print it out
        st.markdown(f"• {dataset_stats['days']} days ({start_date_fmt} - {end_date_fmt})")

    # Define filter functions
    def apply_all_filters():
        # Store the original unfiltered data if not already stored
        if 'original_df' not in st.session_state:
            st.session_state.original_df = df.copy()
        
        # Start with the original data
        filtered_df = st.session_state.original_df.copy()
        
        # Convert date objects to pandas Timestamp for comparison
        start_datetime = pd.Timestamp(start_date)
        end_datetime = pd.Timestamp(end_date)
        
        # Apply date filter - comparing datetime to datetime
        filtered_df = filtered_df[(filtered_df["Timestamp"] >= start_datetime) & 
                                (filtered_df["Timestamp"] <= end_datetime + pd.Timedelta(days=1))]
        
        # Apply behavior filter if behaviors selected
        if selected_behaviors:
            filtered_df = filtered_df[filtered_df["BehaviorType"].isin(selected_behaviors)]
        
        # Apply category filter if categories selected
        if selected_category_ids:
            filtered_df = filtered_df[filtered_df["CategoryID"].isin(selected_category_ids)]
        
        # Return the filtered dataframe
        return filtered_df

    def reset_filters():
        # Reset to original data if it exists
        if 'original_df' in st.session_state:
            return st.session_state.original_df.copy()
        else:
            return load_data_func(data_path)

    # Apply filters based on sidebar selections
    filtered_df = df
    if apply_filters_button:
        filtered_df = apply_all_filters()
    elif reset_filters_button:
        filtered_df = reset_filters()
        
    return filtered_df