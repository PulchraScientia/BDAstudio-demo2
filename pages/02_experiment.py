import streamlit as st
import pandas as pd
import uuid
import datetime
import json
from components.sidebar import render_sidebar
from components.materials_input import render_materials_input
from components.dataset_selector import render_dataset_selector
from components.experiment_results import render_experiment_results
from utils.sql_validator import validate_sql

# Initialize page
st.set_page_config(
    page_title="BDA Studio - Experiments",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Render sidebar
render_sidebar()

# Check if user has selected a workspace
if not st.session_state.current_workspace:
    st.warning("Please select or create a workspace first")
    st.stop()

# Initialize session state for this page
if 'experiment_tab' not in st.session_state:
    st.session_state.experiment_tab = "list"
if 'current_experiment' not in st.session_state:
    st.session_state.current_experiment = None
if 'selected_dataset' not in st.session_state:
    st.session_state.selected_dataset = None
if 'selected_material' not in st.session_state:
    st.session_state.selected_material = None
if 'submenu' in st.session_state:
    # Support navigation from sidebar sub-menu
    if st.session_state.submenu == "datasets":
        st.session_state.experiment_tab = "datasets"
    elif st.session_state.submenu == "materials":
        st.session_state.experiment_tab = "materials"
    # Clear after navigation
    del st.session_state.submenu

# Main experiments page
st.title("Experiments")

# Tabs for different experiment functions
tabs = ["List", "Create", "Datasets", "Materials"]
tab_list, tab_create, tab_datasets, tab_materials = st.tabs(tabs)

# Implement dataset management tab
with tab_datasets:
    st.header("Datasets Management")
    
    # Mock BigQuery dataset selection
    st.subheader("Select from BigQuery Projects")
    
    col1, col2 = st.columns(2)
    with col1:
        project = st.selectbox("Project", ["my-gcp-project", "shared-analytics-project"])
    with col2:
        dataset = st.selectbox("Dataset", ["sales_data", "marketing_data", "customer_data"])
    
    # Tables selector with metadata
    tables_data = {
        "sales_data": [
            {"name": "transactions", "description": "Daily sales transactions", "rows": "1.2M", "last_updated": "2023-12-01"},
            {"name": "products", "description": "Product catalog", "rows": "5.3K", "last_updated": "2023-11-15"}
        ],
        "marketing_data": [
            {"name": "campaigns", "description": "Marketing campaigns", "rows": "350", "last_updated": "2023-12-05"},
            {"name": "ad_performance", "description": "Advertisement performance metrics", "rows": "28.5K", "last_updated": "2023-12-10"}
        ],
        "customer_data": [
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
        
        if st.button("Save Dataset Descriptions"):
            st.success("Dataset descriptions saved to workspace!")
            # Here we would actually save the edited descriptions
            # For the demo, we'll just update the session state
            selected_dataset = {
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
    else:
        st.info("No datasets saved in this workspace yet")

# Implement materials management tab
with tab_materials:
    st.header("Materials Management")
    
    # Create new material
    with st.expander("Create New Material", expanded=True):
        material_name = st.text_input("Material Name")
        
        # Training set input section
        st.subheader("Training Set")
        st.info("Paste your training data (natural language query and SQL pairs)")
        
        train_col1, train_col2 = st.columns(2)
        with train_col1:
            st.markdown("**Natural Language Query**")
            train_nl = st.text_area("Natural Language (Training)", 
                                  placeholder="Enter natural language queries, one per line", 
                                  height=200)
        with train_col2:
            st.markdown("**SQL Query**")
            train_sql = st.text_area("SQL (Training)", 
                                   placeholder="Enter corresponding SQL queries, one per line", 
                                   height=200)
        
        # Test set input section
        st.subheader("Test Set")
        st.info("Paste your test data (natural language query and SQL pairs)")
        
        test_col1, test_col2 = st.columns(2)
        with test_col1:
            st.markdown("**Natural Language Query**")
            test_nl = st.text_area("Natural Language (Test)", 
                                 placeholder="Enter natural language queries, one per line", 
                                 height=200)
        with test_col2:
            st.markdown("**SQL Query**")
            test_sql = st.text_area("SQL (Test)", 
                                  placeholder="Enter corresponding SQL queries, one per line", 
                                  height=200)
        
        # Knowledge data input section
        st.subheader("Knowledge Data")
        st.info("Paste domain knowledge to help the model understand your data")
        knowledge_data = st.text_area("Knowledge Data", 
                                    placeholder="Enter domain knowledge data", 
                                    height=200)
        
        # Validate and save
        if st.button("Validate and Save Material"):
            if material_name and train_nl and train_sql and test_nl and test_sql:
                # Parse and validate input
                train_nl_lines = train_nl.strip().split('\n')
                train_sql_lines = train_sql.strip().split('\n')
                test_nl_lines = test_nl.strip().split('\n')
                test_sql_lines = test_sql.strip().split('\n')
                
                # Check if counts match
                if len(train_nl_lines) != len(train_sql_lines):
                    st.error("Number of training natural language queries must match number of SQL queries")
                elif len(test_nl_lines) != len(test_sql_lines):
                    st.error("Number of test natural language queries must match number of SQL queries")
                else:
                    # Validate SQL queries (mock validation)
                    invalid_sql = []
                    for i, sql in enumerate(train_sql_lines + test_sql_lines):
                        if not validate_sql(sql):
                            dataset = "train" if i < len(train_sql_lines) else "test"
                            idx = i if i < len(train_sql_lines) else i - len(train_sql_lines)
                            invalid_sql.append(f"{dataset} query #{idx+1}: {sql[:50]}...")
                    
                    if invalid_sql:
                        st.error("Invalid SQL queries detected:")
                        for err in invalid_sql:
                            st.write(f"- {err}")
                    else:
                        # Create material
                        new_material = {
                            "id": str(uuid.uuid4()),
                            "name": material_name,
                            "workspace_id": st.session_state.current_workspace['id'],
                            "training_set": [{
                                "nl": nl.strip(),
                                "sql": sql.strip()
                            } for nl, sql in zip(train_nl_lines, train_sql_lines)],
                            "test_set": [{
                                "nl": nl.strip(),
                                "sql": sql.strip()
                            } for nl, sql in zip(test_nl_lines, test_sql_lines)],
                            "knowledge_data": knowledge_data,
                            "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        }
                        
                        st.session_state.materials.append(new_material)
                        st.session_state.selected_material = new_material
                        st.success(f"Material '{material_name}' created successfully!")
            else:
                st.warning("Please fill all required fields")
    
    # Display existing materials
    st.subheader("Existing Materials")
    workspace_materials = [m for m in st.session_state.materials 
                         if m['workspace_id'] == st.session_state.current_workspace['id']]
    
    if workspace_materials:
        for material in workspace_materials:
            with st.expander(f"{material['name']} ({len(material['training_set'])} train, {len(material['test_set'])} test)"):
                st.write(f"Created: {material['created_at']}")
                
                # Sample of the material
                st.markdown("**Sample Training Data:**")
                train_sample = material['training_set'][:2]
                for item in train_sample:
                    st.markdown(f"**NL:** {item['nl']}")
                    st.markdown(f"**SQL:** `{item['sql']}`")
                
                if st.button("Use This Material", key=f"use_material_{material['id']}"):
                    st.session_state.selected_material = material
                    st.success(f"Selected material: {material['name']}")
    else:
        st.info("No materials created in this workspace yet")

# Implement experiment creation tab
with tab_create:
    st.header("Create Experiment")
    
    # Check if dataset and material are selected
    if not st.session_state.selected_dataset:
        st.warning("Please select a dataset first under the Datasets tab")
    
    if not st.session_state.selected_material:
        st.warning("Please select or create materials first under the Materials tab")
    
    if st.session_state.selected_dataset and st.session_state.selected_material:
        # Display current selections
        st.subheader("Selected Components")
        
        col1, col2 = st.columns(2)
        with col1:
            st.info(f"**Dataset:** {st.session_state.selected_dataset['project']}.{st.session_state.selected_dataset['dataset']}")
            st.write(f"Tables: {', '.join([t['name'] for t in st.session_state.selected_dataset['tables']])}")
        
        with col2:
            st.info(f"**Material:** {st.session_state.selected_material['name']}")
            st.write(f"Training samples: {len(st.session_state.selected_material['training_set'])}")
            st.write(f"Test samples: {len(st.session_state.selected_material['test_set'])}")
        
        # Experiment settings
        st.subheader("Experiment Settings")
        
        exp_name = st.text_input("Experiment Name", f"Experiment-{len(st.session_state.experiments)+1}")
        exp_desc = st.text_area("Description", "Testing natural language to SQL conversion")
        
        # Advanced settings (could be expanded)
        with st.expander("Advanced Settings"):
            st.slider("Temperature", min_value=0.0, max_value=1.0, value=0.7, step=0.1)
            st.number_input("Max Tokens", min_value=100, max_value=4000, value=1000, step=100)
        
        # Create experiment button
        if st.button("Create and Run Experiment"):
            # Create a new experiment
            new_experiment = {
                "id": str(uuid.uuid4()),
                "name": exp_name,
                "description": exp_desc,
                "workspace_id": st.session_state.current_workspace['id'],
                "dataset_id": st.session_state.selected_dataset['id'] if 'id' in st.session_state.selected_dataset else None,
                "dataset": st.session_state.selected_dataset,
                "material_id": st.session_state.selected_material['id'],
                "material": st.session_state.selected_material,
                "status": "completed",  # For demo purposes, we'll set it as completed
                "results": {
                    "accuracy": 0.85,  # Mock results
                    "test_results": []
                },
                "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            # Generate mock test results
            for test_item in st.session_state.selected_material['test_set']:
                # For demo purposes, randomly mark some as correct and some as wrong
                is_correct = hash(test_item['nl']) % 4 != 0  # 75% correct rate
                
                generated_sql = test_item['sql']
                if not is_correct:
                    # Slightly modify the SQL to simulate an error
                    if "WHERE" in generated_sql:
                        generated_sql = generated_sql.replace("WHERE", "WHERE LOWER(")
                        if "=" in generated_sql:
                            parts = generated_sql.split("=", 1)
                            generated_sql = f"{parts[0]}) ={parts[1]}"
                
                new_experiment['results']['test_results'].append({
                    "nl": test_item['nl'],
                    "expected_sql": test_item['sql'],
                    "generated_sql": generated_sql,
                    "is_correct": is_correct
                })
            
            # Add to session state
            st.session_state.experiments.append(new_experiment)
            st.session_state.current_experiment = new_experiment
            
            # Navigate to list tab to see results
            st.session_state.experiment_tab = "list"
            st.success(f"Experiment '{exp_name}' created and executed successfully!")
            st.rerun()

# Implement experiment list tab
with tab_list:
    st.header("Experiment List")
    
    # Filter experiments for current workspace
    workspace_experiments = [e for e in st.session_state.experiments 
                          if e['workspace_id'] == st.session_state.current_workspace['id']]
    
    if not workspace_experiments:
        st.info("No experiments created yet in this workspace. Create one in the 'Create' tab.")
    else:
        # Create a dataframe for experiments
        exp_data = []
        for exp in workspace_experiments:
            exp_data.append({
                "ID": exp['id'],
                "Name": exp['name'],
                "Dataset": f"{exp['dataset']['project']}.{exp['dataset']['dataset']}",
                "Material": exp['material']['name'],
                "Accuracy": f"{exp['results']['accuracy'] * 100:.1f}%",
                "Created": exp['created_at'],
                "Status": exp['status']
            })
        
        exp_df = pd.DataFrame(exp_data)
        st.dataframe(
            exp_df,
            column_config={
                "ID": None,  # Hide ID column
                "Name": "Experiment Name",
                "Status": st.column_config.SelectboxColumn(
                    "Status",
                    options=["completed", "failed", "running"],
                    width="small"
                ),
                "Accuracy": st.column_config.ProgressColumn(
                    "Accuracy",
                    min_value=0,
                    max_value=100,
                    format="%f%%",
                ),
            },
            use_container_width=True,
            hide_index=True
        )
        
        # View details of selected experiment
        selected_exp_name = st.selectbox("Select experiment for details", 
                                      ["Select an experiment"] + [exp["name"] for exp in workspace_experiments])
        
        if selected_exp_name != "Select an experiment":
            # Find the selected experiment
            for exp in workspace_experiments:
                if exp["name"] == selected_exp_name:
                    selected_exp = exp
                    break
            
            # Display experiment details
            st.subheader(f"Experiment: {selected_exp['name']}")
            
            # Display dataset and material info
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"**Dataset:** {selected_exp['dataset']['project']}.{selected_exp['dataset']['dataset']}")
                st.markdown(f"**Created:** {selected_exp['created_at']}")
            with col2:
                st.markdown(f"**Material:** {selected_exp['material']['name']}")
                st.markdown(f"**Status:** {selected_exp['status']}")
            
            # Test results tab
            st.subheader("Test Results")
            
            # Create dataframe for test results
            test_results = []
            for idx, res in enumerate(selected_exp['results']['test_results']):
                test_results.append({
                    "idx": idx,
                    "Query": res['nl'],
                    "Generated SQL": res['generated_sql'][:50] + "...",
                    "Correct": "✅" if res['is_correct'] else "❌"
                })
            
            test_df = pd.DataFrame(test_results)
            selected_result = st.dataframe(
                test_df,
                column_config={
                    "idx": None,  # Hide index column
                    "Query": st.column_config.TextColumn("Natural Language Query"),
                    "Generated SQL": st.column_config.TextColumn("Generated SQL"),
                    "Correct": "Status"
                },
                use_container_width=True,
                hide_index=True
                # selection="single" 인자 제거
            )
            
            # Show detail of selected test result
            for _, row in test_df.iterrows():
                if st.button(f"상세 보기: {row['Query'][:30]}...", key=f"detail_{row['idx']}"):
                    idx = row['idx']
                result = selected_exp['results']['test_results'][idx]
                
                st.subheader("Detailed Comparison")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("**Expected SQL**")
                    st.code(result['expected_sql'], language="sql")
                
                with col2:
                    st.markdown("**Generated SQL**")
                    st.code(result['generated_sql'], language="sql")
                
                # For demo, we'll just highlight some differences manually
                if not result['is_correct']:
                    st.error("Differences detected!")
                    # This would be replaced with real diff highlighting
                    st.info("Hint: Check the WHERE clause conditions")
            
            # Action buttons
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Deploy as Assistant", use_container_width=True):
                    # Create a new assistant
                    new_assistant = {
                        "id": str(uuid.uuid4()),
                        "name": f"Assistant from {selected_exp['name']}",
                        "description": f"Created from experiment {selected_exp['name']}",
                        "workspace_id": st.session_state.current_workspace['id'],
                        "experiment_id": selected_exp['id'],
                        "dataset": selected_exp['dataset'],
                        "material": selected_exp['material'],
                        "version": 1,
                        "status": "active",
                        "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    
                    # Add to session state
                    st.session_state.assistants.append(new_assistant)
                    st.success(f"Assistant created from experiment '{selected_exp['name']}'!")
                    
                    # Offer to navigate to the assistants page
                    if st.button("Go to Assistants Page"):
                        st.switch_page("pages/03_assistant.py")
            
            with col2:
                if st.button("Retry Experiment", use_container_width=True):
                    # Set up for a new experiment with the same data
                    st.session_state.selected_dataset = selected_exp['dataset']
                    st.session_state.selected_material = selected_exp['material']
                    # Switch to create tab
                    tab_create.active = True
                    st.rerun()