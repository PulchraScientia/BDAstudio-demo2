import streamlit as st
import pandas as pd
import uuid
import datetime
from components.sidebar import render_sidebar
from utils.sql_validator import validate_sql

# Initialize page
st.set_page_config(
    page_title="BDA Studio - Materials",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded"
)


# Render sidebar
render_sidebar()

# Check if user has selected a workspace
if not st.session_state.current_workspace:
    st.warning("Please select or create a workspace first")
    st.stop()

# Initialize session states for this page
if 'show_train_editor' not in st.session_state:
    st.session_state.show_train_editor = False
if 'show_test_editor' not in st.session_state:
    st.session_state.show_test_editor = False
if 'temp_train_data' not in st.session_state:
    st.session_state.temp_train_data = pd.DataFrame({"natural_language": [""], "sql": [""]})
if 'temp_test_data' not in st.session_state:
    st.session_state.temp_test_data = pd.DataFrame({"natural_language": [""], "sql": [""]})

# Function to toggle train editor
def toggle_train_editor():
    st.session_state.show_train_editor = not st.session_state.show_train_editor

# Function to toggle test editor
def toggle_test_editor():
    st.session_state.show_test_editor = not st.session_state.show_test_editor

# Function to save train data
def save_train_data():
    st.session_state.temp_train_data = st.session_state.edited_train_data
    st.session_state.show_train_editor = False

# Function to save test data
def save_test_data():
    st.session_state.temp_test_data = st.session_state.edited_test_data
    st.session_state.show_test_editor = False

# Main materials page
st.title("Materials Management")
st.write("Create and manage training and testing materials for your natural language to SQL experiments.")

# Create new material section
with st.expander("Create New Material", expanded=True):
    material_name = st.text_input("Material Name")
    
    # Training set input section
    st.subheader("Training Set")
    st.info("Input natural language queries and corresponding SQL queries for training.")
    
    # Show current training data
    if not st.session_state.temp_train_data.empty and len(st.session_state.temp_train_data) > 0 and st.session_state.temp_train_data.iloc[0]['natural_language'] != "":
        st.write(f"Training examples: {len(st.session_state.temp_train_data)}")
        with st.expander("Preview Training Data"):
            st.dataframe(st.session_state.temp_train_data, use_container_width=True)
    
    # Button to open the editor
    st.button("Edit Training Data", on_click=toggle_train_editor)
    
    # Excel-like popup editor for training data
    if st.session_state.show_train_editor:
        st.subheader("Training Data Editor")
        st.write("Add your training examples below. Each row represents one query pair.")
        
        # Initialize with current data
        if 'edited_train_data' not in st.session_state:
            st.session_state.edited_train_data = st.session_state.temp_train_data.copy()
        
        # Data editor with Excel-like functionality
        st.session_state.edited_train_data = st.data_editor(
            st.session_state.edited_train_data,
            column_config={
                "natural_language": st.column_config.TextColumn("Natural Language Query", width="large"),
                "sql": st.column_config.TextColumn("SQL Query", width="large")
            },
            num_rows="dynamic",
            use_container_width=True,
            hide_index=True,
            key="train_data_editor"
        )
        
        # Save and cancel buttons
        col1, col2 = st.columns(2)
        with col1:
            st.button("Save Training Data", on_click=save_train_data, type="primary")
        with col2:
            if st.button("Cancel", on_click=toggle_train_editor):
                if 'edited_train_data' in st.session_state:
                    del st.session_state.edited_train_data
    
    # Test set input section
    st.subheader("Test Set")
    st.info("Input natural language queries and corresponding SQL queries for testing.")
    
    # Show current test data
    if not st.session_state.temp_test_data.empty and len(st.session_state.temp_test_data) > 0 and st.session_state.temp_test_data.iloc[0]['natural_language'] != "":
        st.write(f"Test examples: {len(st.session_state.temp_test_data)}")
        with st.expander("Preview Test Data"):
            st.dataframe(st.session_state.temp_test_data, use_container_width=True)
    
    # Button to open the editor
    st.button("Edit Test Data", on_click=toggle_test_editor)
    
    # Excel-like popup editor for test data
    if st.session_state.show_test_editor:
        st.subheader("Test Data Editor")
        st.write("Add your test examples below. Each row represents one query pair.")
        
        # Initialize with current data
        if 'edited_test_data' not in st.session_state:
            st.session_state.edited_test_data = st.session_state.temp_test_data.copy()
        
        # Data editor with Excel-like functionality
        st.session_state.edited_test_data = st.data_editor(
            st.session_state.edited_test_data,
            column_config={
                "natural_language": st.column_config.TextColumn("Natural Language Query", width="large"),
                "sql": st.column_config.TextColumn("SQL Query", width="large")
            },
            num_rows="dynamic",
            use_container_width=True,
            hide_index=True,
            key="test_data_editor"
        )
        
        # Save and cancel buttons
        col1, col2 = st.columns(2)
        with col1:
            st.button("Save Test Data", on_click=save_test_data, type="primary")
        with col2:
            if st.button("Cancel", key="cancel_test_edit", on_click=toggle_test_editor):
                if 'edited_test_data' in st.session_state:
                    del st.session_state.edited_test_data
    
    # Knowledge data input section
    st.subheader("Knowledge Data")
    st.info("Input domain knowledge to help the model understand your data context.")
    
    knowledge_data = st.text_area(
        "Knowledge Data", 
        placeholder="Enter domain knowledge data that helps understand the database structure, relationships, and business rules.",
        height=150
    )
    
    # Validate and save material
    if st.button("Validate and Save Material"):
        if material_name and not st.session_state.temp_train_data.empty and not st.session_state.temp_test_data.empty:
            # Check if we have actual data
            has_train_data = (len(st.session_state.temp_train_data) > 0 and 
                           st.session_state.temp_train_data.iloc[0]['natural_language'] != "")
            has_test_data = (len(st.session_state.temp_test_data) > 0 and 
                          st.session_state.temp_test_data.iloc[0]['natural_language'] != "")
            
            if not has_train_data:
                st.error("Please add at least one training example")
            elif not has_test_data:
                st.error("Please add at least one test example")
            else:
                # Validate SQL queries (mock validation)
                invalid_sql = []
                
                # Validate training SQL
                for idx, row in st.session_state.temp_train_data.iterrows():
                    if not validate_sql(row['sql']):
                        invalid_sql.append(f"Training query #{idx+1}: {row['sql'][:50]}...")
                
                # Validate test SQL
                for idx, row in st.session_state.temp_test_data.iterrows():
                    if not validate_sql(row['sql']):
                        invalid_sql.append(f"Test query #{idx+1}: {row['sql'][:50]}...")
                
                if invalid_sql:
                    st.error("Invalid SQL queries detected:")
                    for err in invalid_sql:
                        st.write(f"- {err}")
                else:
                    # Convert dataframes to the format we need
                    training_set = []
                    for _, row in st.session_state.temp_train_data.iterrows():
                        training_set.append({
                            "nl": row['natural_language'],
                            "sql": row['sql']
                        })
                    
                    test_set = []
                    for _, row in st.session_state.temp_test_data.iterrows():
                        test_set.append({
                            "nl": row['natural_language'],
                            "sql": row['sql']
                        })
                    
                    # Create new material
                    new_material = {
                        "id": str(uuid.uuid4()),
                        "name": material_name,
                        "workspace_id": st.session_state.current_workspace['id'],
                        "training_set": training_set,
                        "test_set": test_set,
                        "knowledge_data": knowledge_data,
                        "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    
                    # Add to session state
                    st.session_state.materials.append(new_material)
                    st.session_state.selected_material = new_material
                    
                    # Reset temp data
                    st.session_state.temp_train_data = pd.DataFrame({"natural_language": [""], "sql": [""]})
                    st.session_state.temp_test_data = pd.DataFrame({"natural_language": [""], "sql": [""]})
                    
                    st.success(f"Material '{material_name}' created successfully!")
                    st.rerun()
        else:
            st.warning("Please fill in material name and add training and test data.")

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
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("Use This Material", key=f"use_material_{material['id']}"):
                    st.session_state.selected_material = material
                    st.success(f"Selected material: {material['name']}")
            
            with col2:
                if st.button("Edit", key=f"edit_material_{material['id']}"):
                    # Load material data into temp data for editing
                    train_data = []
                    for item in material['training_set']:
                        train_data.append({
                            "natural_language": item['nl'],
                            "sql": item['sql']
                        })
                    
                    test_data = []
                    for item in material['test_set']:
                        test_data.append({
                            "natural_language": item['nl'],
                            "sql": item['sql']
                        })
                    
                    st.session_state.temp_train_data = pd.DataFrame(train_data)
                    st.session_state.temp_test_data = pd.DataFrame(test_data)
                    st.success(f"Loaded material '{material['name']}' for editing. Scroll up to the Create New Material section.")
            
            with col3:
                if st.button("Delete", key=f"delete_material_{material['id']}"):
                    # Remove material from session state
                    st.session_state.materials = [m for m in st.session_state.materials if m['id'] != material['id']]
                    
                    # If this was the selected material, reset selection
                    if st.session_state.get('selected_material') and st.session_state.selected_material['id'] == material['id']:
                        st.session_state.selected_material = None
                    
                    st.success(f"Material '{material['name']}' deleted.")
                    st.rerun()
else:
    st.info("No materials created in this workspace yet.")

# Quick action to create experiment
st.divider()
if st.session_state.get('selected_material'):
    if st.button("Create Experiment with Selected Material", use_container_width=True):
        st.switch_page("pages/02_experiment.py")