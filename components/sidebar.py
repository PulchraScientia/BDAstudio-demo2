import streamlit as st
import uuid

def render_sidebar():
    with st.sidebar:
        st.title("BDA Studio")
        
        # User info
        st.write(f"Logged in as: {st.session_state.user['name']}")
        st.divider()
        
        # Workspace selector/creator
        st.subheader("Workspace")
        
        # Create new workspace
        with st.expander("Create New Workspace"):
            workspace_name = st.text_input("Workspace Name")
            workspace_desc = st.text_area("Description")
            
            if st.button("Create Workspace"):
                if workspace_name:
                    new_workspace = {
                        "id": str(uuid.uuid4()),
                        "name": workspace_name,
                        "description": workspace_desc,
                        "created_by": st.session_state.user["email"]
                    }
                    st.session_state.workspaces.append(new_workspace)
                    st.session_state.current_workspace = new_workspace
                    st.success(f"Workspace '{workspace_name}' created!")
                    st.rerun()
                else:
                    st.warning("Please enter a workspace name")
        
        # Select existing workspace
        if st.session_state.workspaces:
            workspace_options = ["Select Workspace"] + [ws["name"] for ws in st.session_state.workspaces]
            selected_workspace = st.selectbox("Select Workspace", workspace_options)
            
            if selected_workspace != "Select Workspace":
                for ws in st.session_state.workspaces:
                    if ws["name"] == selected_workspace:
                        st.session_state.current_workspace = ws
                        break
        
        st.divider()
        
        # Navigation menu
        st.subheader("Navigation")
        
        # Main menu links
        if st.button("🏠 Home", use_container_width=True):
            st.switch_page("main.py")
        
        # Enable other options only if workspace is selected
        if st.session_state.current_workspace:
            if st.button("🧪 Experiments", use_container_width=True):
                st.switch_page("pages/02_experiment.py")
                
            # Experiment sub-menu
            with st.expander("Experiment Settings"):
                if st.button("📊 Datasets", use_container_width=True):
                    st.session_state.submenu = "datasets"
                    st.switch_page("pages/02_experiment.py")
                
                if st.button("📝 Materials", use_container_width=True):
                    st.session_state.submenu = "materials"
                    st.switch_page("pages/02_experiment.py")
            
            if st.button("🤖 Assistants", use_container_width=True):
                st.switch_page("pages/03_assistant.py")
                
        st.divider()
                
        # Help section
        with st.expander("Help"):
            st.markdown("""
            **Quick Help**
            
            - Create a workspace first
            - Set up datasets and materials
            - Create an experiment
            - Evaluate and deploy as assistant
            
            [Documentation](https://example.com/docs)
            """)
            
        # Settings and logout
        st.divider()
        if st.button("⚙️ Settings", use_container_width=True):
            st.info("Settings functionality would go here")
            
        if st.button("🚪 Logout", use_container_width=True):
            # This would normally clear session and redirect to login
            st.info("Logout functionality would go here")