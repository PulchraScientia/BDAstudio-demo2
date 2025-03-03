import streamlit as st
import pandas as pd
import uuid
from components.sidebar import render_sidebar
from components.dataset_selector import render_dataset_selector

# Initialize page
st.set_page_config(
    page_title="BDA Studio - Datasets",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 네비게이션 메뉴 숨기기
hide_streamlit_style = """
<style>
#MainMenu {visibility: hidden;}
div[data-testid="stSidebarNav"] {display: none;}
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)


# Render sidebar
render_sidebar()

# Check if user has selected a workspace
if not st.session_state.current_workspace:
    st.warning("Please select or create a workspace first")
    st.stop()

# Main datasets page
st.title("Datasets Management")
st.write("Configure and manage datasets for your workspace.")

# Mock BigQuery dataset selection
st.subheader("Select from BigQuery DataSets")

col1, col2 = st.columns(2)
with col1:
    project = st.selectbox("Dataset", ["my-gcp-dataset", "shared-analytics-dataset"])
with col2:
    dataset = st.selectbox("Table", ["sales_table", "marketing_table", "customer_table"])

# Tables selector with metadata
tables_data = {
    "sales_table": [
        {"name": "transactions", "description": "Daily sales transactions", "rows": "1.2M", "last_updated": "2023-12-01"},
        {"name": "products", "description": "Product catalog", "rows": "5.3K", "last_updated": "2023-11-15"}
    ],
    "marketing_table": [
        {"name": "campaigns", "description": "Marketing campaigns", "rows": "350", "last_updated": "2023-12-05"},
        {"name": "ad_performance", "description": "Advertisement performance metrics", "rows": "28.5K", "last_updated": "2023-12-10"}
    ],
    "customer_table": [
        {"name": "customers", "description": "Customer information", "rows": "2.1M", "last_updated": "2023-11-25"},
        {"name": "interactions", "description": "Customer interactions and touchpoints", "rows": "15.3M", "last_updated": "2023-12-15"}
    ]
}

st.subheader("Available Tables")

# Show tables for selected dataset
if dataset in tables_data:
    table_df = pd.DataFrame(tables_data[dataset])
    
    # Enable editing of descriptions
    edited_df = st.data_editor(
        table_df,
        column_config={
            "name": "Table Name",
            "description": st.column_config.TextColumn("Description", width="large"),
            "rows": "Row Count",
            "last_updated": "Last Updated"
        },
        use_container_width=True,
        num_rows="fixed",
        hide_index=True,
        key="table_editor"
    )
    
    if st.button("Save Table Descriptions"):
        st.success("Table descriptions saved to workspace!")
        # Here we would actually save the edited descriptions
        # For the demo, we'll just update the session state
        selected_dataset = {
            "id": str(uuid.uuid4()),
            "project": project,
            "dataset": dataset,
            "tables": edited_df.to_dict('records'),
            "workspace_id": st.session_state.current_workspace['id']
        }
        
        # Check if this dataset already exists in session state
        dataset_exists = False
        for i, ds in enumerate(st.session_state.datasets):
            if ds["project"] == project and ds["dataset"] == dataset:
                st.session_state.datasets[i] = selected_dataset
                dataset_exists = True
                break
                
        if not dataset_exists:
            st.session_state.datasets.append(selected_dataset)
        
        st.session_state.selected_dataset = selected_dataset
else:
    st.info("Select a dataset to view available tables")
    
# Show a list of saved datasets in this workspace
st.subheader("Workspace Datasets")
workspace_datasets = [ds for ds in st.session_state.datasets 
                    if ds['workspace_id'] == st.session_state.current_workspace['id']]

if workspace_datasets:
    for ds in workspace_datasets:
        with st.expander(f"{ds['project']}.{ds['dataset']}"):
            st.write(f"Tables: {', '.join([t['name'] for t in ds['tables']])}")
            if st.button("Use This Dataset", key=f"use_{ds['project']}_{ds['dataset']}"):
                st.session_state.selected_dataset = ds
                st.success(f"Selected dataset: {ds['project']}.{ds['dataset']}")
                
            # View schema button
            if st.button("View Schema", key=f"schema_{ds['project']}_{ds['dataset']}"):
                st.subheader(f"Schema for {ds['project']}.{ds['dataset']}")
                
                # Display schema for each table
                for table in ds['tables']:
                    st.write(f"**{table['name']}**")
                    st.write(f"Description: {table['description']}")
                    st.write(f"Rows: {table['rows']}")
                    
                    # Mock schema
                    schema_df = pd.DataFrame([
                        {"column": "id", "type": "INTEGER", "mode": "REQUIRED", "description": "Primary key"},
                        {"column": "name", "type": "STRING", "mode": "REQUIRED", "description": "Item name"},
                        {"column": "value", "type": "FLOAT", "mode": "NULLABLE", "description": "Item value"},
                        {"column": "created_at", "type": "TIMESTAMP", "mode": "REQUIRED", "description": "Creation timestamp"}
                    ])
                    
                    st.dataframe(schema_df, use_container_width=True, hide_index=True)
else:
    st.info("No datasets saved in this workspace yet")

# Quick action to create experiment
st.divider()
if st.session_state.selected_dataset:
    if st.button("Create Experiment with Selected Dataset", use_container_width=True):
        # 실험 페이지로 이동할 때 탭을 "create"로 설정
        st.session_state.experiment_tab = "create"
        st.switch_page("pages/02_experiment.py")