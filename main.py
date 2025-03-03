import streamlit as st
from components.sidebar import render_sidebar
import utils.session_state as ss

# Page configuration
st.set_page_config(
    page_title="BDA Studio",
    page_icon="🔎",
    layout="wide",
    initial_sidebar_state="expanded"
)

ss.initialize_session_state()

# Add some demo data for testing
ss.add_demo_data()

# Main app
def main():
    # Render sidebar
    render_sidebar()
    
    # Main content - Homepage
    st.title("BDA Studio")
    st.subheader("Natural Language to SQL Assistant Platform")
    
    if not st.session_state.current_workspace:
        st.info("Please create or select a workspace from the sidebar to get started.")
        
        # Welcome section
        st.markdown("""
        ## Welcome to BDA Studio
        
        BDA Studio helps you create and fine-tune natural language to SQL assistants for your BigQuery datasets.
        
        ### Getting Started:
        1. Create a new workspace or select an existing one
        2. Create an experiment by selecting datasets and materials
        3. Evaluate your experiment results
        4. Deploy successful experiments as assistants
        5. Chat with your assistants using natural language
        """)
        
        # Mock stats
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(label="Your Workspaces", value=len(st.session_state.workspaces))
        with col2:
            st.metric(label="Your Experiments", value=len(st.session_state.experiments))
        with col3:
            st.metric(label="Your Assistants", value=len(st.session_state.assistants))
    else:
        # Display current workspace information
        st.write(f"Current Workspace: **{st.session_state.current_workspace['name']}**")
        st.write(f"Description: {st.session_state.current_workspace['description']}")
        
        # Workspace dashboard
        col1, col2, col3 = st.columns(3)
        
        # Count experiments in this workspace
        workspace_experiments = [e for e in st.session_state.experiments 
                              if e['workspace_id'] == st.session_state.current_workspace['id']]
        
        # Count assistants in this workspace
        workspace_assistants = [a for a in st.session_state.assistants 
                             if a['workspace_id'] == st.session_state.current_workspace['id']]
        
        with col1:
            st.metric(label="Experiments", value=len(workspace_experiments))
        with col2:
            st.metric(label="Assistants", value=len(workspace_assistants))
        with col3:
            # Just a placeholder metric
            st.metric(label="Success Rate", value="85%")
        
        # Quick actions
        st.subheader("Quick Actions")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Create New Experiment", use_container_width=True):
                st.switch_page("pages/02_experiment.py")
        with col2:
            if st.button("Browse Assistants", use_container_width=True):
                st.switch_page("pages/03_assistant.py")

if __name__ == "__main__":
    main()