import streamlit as st
import pandas as pd
import uuid
import datetime
from components.sidebar import render_sidebar

# Initialize page
st.set_page_config(
    page_title="BDA Studio - Assistants",
    page_icon="🤖",
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
if 'assistant_tab' not in st.session_state:
    st.session_state.assistant_tab = "list"
if 'current_assistant' not in st.session_state:
    st.session_state.current_assistant = None
if 'current_assistant_version' not in st.session_state:
    st.session_state.current_assistant_version = None

# Main assistants page
st.title("Assistants")

# Filter assistants for current workspace
workspace_assistants = [a for a in st.session_state.assistants 
                      if a['workspace_id'] == st.session_state.current_workspace['id']]

if not workspace_assistants:
    st.info("No assistants created yet in this workspace. Create an experiment and deploy it as an assistant.")
    
    # Quick link to create experiment
    if st.button("Create an Experiment"):
        st.switch_page("pages/02_experiment.py")
else:
    # Group assistants by name to track versions
    assistant_groups = {}
    for assist in workspace_assistants:
        name = assist['name']
        if name not in assistant_groups:
            assistant_groups[name] = []
        assistant_groups[name].append(assist)
    
    # Sort each group by version
    for name, group in assistant_groups.items():
        assistant_groups[name] = sorted(group, key=lambda x: x.get('version', 1))
    
    # Create columns for assistant cards
    cols = st.columns(3)
    
    # Display assistant cards
    for idx, (name, assistants) in enumerate(assistant_groups.items()):
        latest = assistants[-1]  # Get the latest version
        
        with cols[idx % 3]:
            with st.container(border=True):
                st.subheader(name)
                st.write(f"Version: {latest.get('version', 1)}")
                st.write(f"Created: {latest['created_at']}")
                st.write(f"Dataset: {latest['dataset']['project']}.{latest['dataset']['dataset']}")
                
                # Version selector for this assistant
                versions = [f"v{a.get('version', 1)}" for a in assistants]
                selected_version = st.selectbox(
                    "Select version", 
                    versions, 
                    index=len(versions)-1,
                    key=f"version_select_{latest['id']}"
                )
                
                # Extract the version number from the string
                selected_v_num = int(selected_version.replace('v', ''))
                
                # Find the assistant with this version
                selected_assistant = next(a for a in assistants if a.get('version', 1) == selected_v_num)
                
                # Chat button
                if st.button("Chat with Assistant", key=f"chat_{latest['id']}"):
                    st.session_state.current_assistant = selected_assistant
                    st.session_state.current_assistant_version = selected_v_num
                    st.switch_page("pages/04_chat.py")
                
                # Show details button
                with st.expander("Show Details"):
                    st.write(f"Description: {selected_assistant.get('description', 'No description')}")
                    st.write(f"Material: {selected_assistant['material']['name']}")
                    st.write(f"Training examples: {len(selected_assistant['material']['training_set'])}")
                    
                    # Information about the dataset and tables
                    st.subheader("Dataset Information")
                    for table in selected_assistant['dataset']['tables']:
                        st.write(f"- {table['name']}: {table['description']}")