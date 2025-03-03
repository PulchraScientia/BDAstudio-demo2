import streamlit as st
import pandas as pd

def render_dataset_selector():
    """Render the dataset selector component"""
    st.subheader("Select Dataset")
    
    # Mock GCP projects and datasets
    projects = ["my-gcp-project", "shared-analytics-project", "customer-insights"]
    
    # Project selection
    selected_project = st.selectbox(
        "GCP Project", 
        projects,
        help="Select a Google Cloud Platform project"
    )
    
    # Mock datasets based on project
    datasets_by_project = {
        "my-gcp-project": ["sales_data", "product_data", "user_activity"],
        "shared-analytics-project": ["marketing_campaigns", "web_analytics", "social_media"],
        "customer-insights": ["customer_profiles", "user_journey", "feedback_data"]
    }
    
    # Dataset selection
    datasets = datasets_by_project.get(selected_project, [])
    selected_dataset = st.selectbox(
        "BigQuery Dataset", 
        datasets,
        help="Select a BigQuery dataset"
    )
    
    # Mock tables based on dataset
    tables_by_dataset = {
        "sales_data": [
            {"name": "transactions", "description": "Customer transaction records", "rows": "1.2M", "last_modified": "2023-12-10"},
            {"name": "sales_reps", "description": "Sales representatives information", "rows": "523", "last_modified": "2023-11-15"},
            {"name": "products", "description": "Product catalog", "rows": "12.5K", "last_modified": "2023-12-01"}
        ],
        "product_data": [
            {"name": "product_catalog", "description": "Complete product information", "rows": "15K", "last_modified": "2023-12-05"},
            {"name": "categories", "description": "Product categories", "rows": "42", "last_modified": "2023-10-20"},
            {"name": "inventory", "description": "Current inventory levels", "rows": "15K", "last_modified": "2023-12-15"}
        ],
        "user_activity": [
            {"name": "page_views", "description": "Website page view events", "rows": "25M", "last_modified": "2023-12-15"},
            {"name": "user_sessions", "description": "User session data", "rows": "4.2M", "last_modified": "2023-12-15"},
            {"name": "clicks", "description": "User click events", "rows": "18M", "last_modified": "2023-12-15"}
        ],
        "marketing_campaigns": [
            {"name": "campaigns", "description": "Marketing campaign details", "rows": "350", "last_modified": "2023-11-30"},
            {"name": "ad_performance", "description": "Ad performance metrics", "rows": "25K", "last_modified": "2023-12-10"},
            {"name": "campaign_spend", "description": "Campaign spending data", "rows": "1.2K", "last_modified": "2023-12-05"}
        ]
    }
    
    # Show tables for the selected dataset
    if selected_dataset in tables_by_dataset:
        st.subheader("Available Tables")
        
        # Convert to DataFrame for display
        tables_df = pd.DataFrame(tables_by_dataset[selected_dataset])
        
        # Allow editing descriptions
        edited_tables = st.data_editor(
            tables_df,
            column_config={
                "name": st.column_config.TextColumn("Table Name"),
                "description": st.column_config.TextColumn("Description", width="large"),
                "rows": st.column_config.TextColumn("Row Count", width="small"),
                "last_modified": st.column_config.TextColumn("Last Modified", width="medium")
            },
            disabled=["name", "rows", "last_modified"],
            use_container_width=True,
            hide_index=True,
            key="tables_editor"
        )
        
        # Return selected dataset info
        return {
            "project": selected_project,
            "dataset": selected_dataset,
            "tables": edited_tables.to_dict('records')
        }
    
    return None