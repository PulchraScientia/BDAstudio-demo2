import streamlit as st
import pandas as pd

def render_materials_input():
    """Render the materials input component"""
    st.subheader("Input Materials")
    
    # Training set
    st.markdown("### Training Set")
    st.info("Copy and paste data from Excel or CSV")
    
    # Create a data editor for training set
    training_data = pd.DataFrame({
        "natural_language": ["", ""],
        "sql": ["", ""]
    })
    
    train_edited = st.data_editor(
        training_data,
        column_config={
            "natural_language": st.column_config.TextColumn("Natural Language Query", width="large"),
            "sql": st.column_config.TextColumn("SQL Query", width="large")
        },
        num_rows="dynamic",
        use_container_width=True,
        hide_index=True,
        key="training_editor"
    )
    
    # Test set
    st.markdown("### Test Set")
    st.info("Copy and paste data from Excel or CSV")
    
    # Create a data editor for test set
    test_data = pd.DataFrame({
        "natural_language": ["", ""],
        "sql": ["", ""]
    })
    
    test_edited = st.data_editor(
        test_data,
        column_config={
            "natural_language": st.column_config.TextColumn("Natural Language Query", width="large"),
            "sql": st.column_config.TextColumn("SQL Query", width="large")
        },
        num_rows="dynamic",
        use_container_width=True,
        hide_index=True,
        key="test_editor"
    )
    
    # Knowledge data
    st.markdown("### Knowledge Data")
    st.info("Add domain-specific knowledge to help the model")
    
    knowledge = st.text_area(
        "Domain Knowledge", 
        "", 
        height=200, 
        help="Add context about your domain that will help the model generate better SQL"
    )
    
    # Return the edited data
    return {
        "training_set": train_edited.to_dict('records'),
        "test_set": test_edited.to_dict('records'),
        "knowledge_data": knowledge
    }