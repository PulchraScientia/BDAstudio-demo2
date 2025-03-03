import streamlit as st
import pandas as pd
import uuid
import datetime
from components.sidebar import render_sidebar

# Initialize page
st.set_page_config(
    page_title="BDA Studio - Workspaces",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Render sidebar
render_sidebar()

# Main workspaces page
st.title("Workspaces")

# Check if user is logged in (for demo, we assume they are)
if 'user' not in st.session_state:
    st.session_state.user = {"name": "Demo User", "email": "demo@example.com"}

# Initialize workspaces list if not present
if 'workspaces' not in st.session_state:
    st.session_state.workspaces = []

# Create two tabs for workspace actions
tab_list, tab_create = st.tabs(["My Workspaces", "Create Workspace"])

# Workspace listing tab
with tab_list:
    st.header("My Workspaces")
    
    if not st.session_state.workspaces:
        st.info("You don't have any workspaces yet. Create one in the 'Create Workspace' tab.")
    else:
        # Display workspaces in a grid
        for idx, workspace in enumerate(st.session_state.workspaces):
            with st.container(border=True):
                st.subheader(workspace["name"])
                st.write(f"Created: {workspace.get('created_at', 'N/A')}")
                st.write(workspace.get("description", "No description"))
                
                # Count items in this workspace
                experiments_count = len([e for e in st.session_state.get('experiments', []) 
                                    if e['workspace_id'] == workspace['id']])
                assistants_count = len([a for a in st.session_state.get('assistants', []) 
                                if a['workspace_id'] == workspace['id']])
                
                col1, col2 = st.columns(2)
                col1.metric("Experiments", experiments_count)
                col2.metric("Assistants", assistants_count)
                
                # Action buttons
                if st.button("Select Workspace", key=f"select_{workspace['id']}"):
                    st.session_state.current_workspace = workspace
                    st.success(f"Selected workspace: {workspace['name']}")
                    st.rerun()
                
                with st.expander("Manage Workspace"):
                    if st.button("Delete Workspace", key=f"delete_{workspace['id']}"):
                        # Confirm deletion
                        st.warning("Are you sure you want to delete this workspace?")
                        confirm_col1, confirm_col2 = st.columns(2)
                        with confirm_col1:
                            if st.button("Yes, Delete", key=f"confirm_delete_{workspace['id']}"):
                                # Remove workspace from session state
                                st.session_state.workspaces = [w for w in st.session_state.workspaces 
                                                        if w['id'] != workspace['id']]
                                
                                # If this was the current workspace, reset current_workspace
                                if (st.session_state.get('current_workspace') and 
                                    st.session_state.current_workspace['id'] == workspace['id']):
                                    st.session_state.current_workspace = None
                                
                                st.success(f"Workspace '{workspace['name']}' deleted!")
                                st.rerun()
                        with confirm_col2:
                            if st.button("Cancel", key=f"cancel_delete_{workspace['id']}"):
                                st.rerun()

# Create workspace tab
with tab_create:
    st.header("Create New Workspace")
    
    with st.form("create_workspace_form"):
        workspace_name = st.text_input("Workspace Name", placeholder="Enter a name for your workspace")
        workspace_desc = st.text_area("Description", placeholder="Describe the purpose of this workspace")
        
        # Team members (would be implemented in a real app)
        st.subheader("Team Members")
        st.info("In a real implementation, you would be able to add team members here.")
        
        # Mock team member input
        team_members = st.text_input("Add Team Members (comma separated emails)", 
                                placeholder="teammate1@example.com, teammate2@example.com")
        
        submitted = st.form_submit_button("Create Workspace")

    # 폼 외부에서 처리
    if submitted:
        if workspace_name:
            # Create new workspace
            new_workspace = {
                "id": str(uuid.uuid4()),
                "name": workspace_name,
                "description": workspace_desc,
                "created_by": st.session_state.user["email"],
                "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "team_members": [email.strip() for email in team_members.split(",")] if team_members else []
            }
            
            # Add to session state
            st.session_state.workspaces.append(new_workspace)
            
            # Set as current workspace
            st.session_state.current_workspace = new_workspace
            
            st.success(f"Workspace '{workspace_name}' created successfully!")
            
            # 이제 폼 외부에 있으므로 정상 작동
            if st.button("Go to Experiments"):
                st.switch_page("pages/02_experiment.py")
        else:
            st.error("Please enter a workspace name")

# Display current workspace if one is selected
if st.session_state.get('current_workspace'):
    st.sidebar.success(f"Current Workspace: {st.session_state.current_workspace['name']}")
    
    # Additional workspace info
    st.sidebar.divider()
    st.sidebar.markdown("### Workspace Info")
    st.sidebar.write(f"**Created by:** {st.session_state.current_workspace.get('created_by', 'Unknown')}")
    st.sidebar.write(f"**Created:** {st.session_state.current_workspace.get('created_at', 'Unknown')}")
    
    # Team members
    if 'team_members' in st.session_state.current_workspace and st.session_state.current_workspace['team_members']:
        st.sidebar.markdown("### Team Members")
        for member in st.session_state.current_workspace['team_members']:
            if member:  # Only show non-empty members
                st.sidebar.write(f"- {member}")