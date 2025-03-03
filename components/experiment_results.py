import streamlit as st
import pandas as pd
import difflib
import html

def render_experiment_results(experiment):
    """Render the experiment results component"""
    if not experiment:
        st.warning("No experiment selected")
        return
    
    st.subheader("Experiment Results")
    
    # Display experiment metadata
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(
            "Accuracy", 
            f"{experiment['results']['accuracy'] * 100:.1f}%",
            help="Percentage of test queries correctly translated to SQL"
        )
    with col2:
        correct_count = sum(1 for r in experiment['results']['test_results'] if r['is_correct'])
        total_count = len(experiment['results']['test_results'])
        st.metric(
            "Correct Queries", 
            f"{correct_count}/{total_count}",
            help="Number of correctly translated queries out of total test queries"
        )
    with col3:
        st.metric(
            "Test Set Size", 
            len(experiment['results']['test_results']),
            help="Total number of test queries"
        )
    
    # Display test results table
    st.markdown("### Test Query Results")
    
    # Create a dataframe for test results
    results_data = []
    for idx, result in enumerate(experiment['results']['test_results']):
        results_data.append({
            "id": idx,
            "Query": result['nl'],
            "Generated SQL": result['generated_sql'][:50] + ("..." if len(result['generated_sql']) > 50 else ""),
            "Correct": "✅" if result['is_correct'] else "❌"
        })
    
    results_df = pd.DataFrame(results_data)
    
    # Display as a selectable dataframe
    selected_rows = st.dataframe(
        results_df,
        column_config={
            "id": None,  # Hide ID column
            "Query": st.column_config.TextColumn("Natural Language Query", width="large"),
            "Generated SQL": st.column_config.TextColumn("Generated SQL", width="large"),
            "Correct": st.column_config.TextColumn("Status", width="small"),
        },
        use_container_width=True,
        hide_index=True,
        selection="single"
    )
    
    # Show details for selected row
    if selected_rows.selected_rows:
        selected_id = selected_rows.selected_rows[0]["id"]
        selected_result = experiment['results']['test_results'][selected_id]
        
        st.markdown("### SQL Comparison")
        
        # Display detailed SQL comparison
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Expected SQL**")
            st.code(selected_result['expected_sql'], language="sql")
        
        with col2:
            st.markdown("**Generated SQL**")
            st.code(selected_result['generated_sql'], language="sql")
        
        # For incorrect answers, show a simple diff
        if not selected_result['is_correct']:
            st.markdown("### Differences")
            
            # Generate HTML diff
            diff = difflib.ndiff(
                selected_result['expected_sql'].splitlines(), 
                selected_result['generated_sql'].splitlines()
            )
            
            # Format diff output for display
            diff_lines = []
            for line in diff:
                if line.startswith('+ '):
                    diff_lines.append(f"<span style='color:green'>**{html.escape(line)}**</span>")
                elif line.startswith('- '):
                    diff_lines.append(f"<span style='color:red'>**{html.escape(line)}**</span>")
                elif line.startswith('? '):
                    # Skip the "?" lines that indicate where changes are
                    continue
                else:
                    diff_lines.append(html.escape(line))
            
            # Display diff
            st.markdown("<pre>" + "<br>".join(diff_lines) + "</pre>", unsafe_allow_html=True)
            
            # Provide a hint
            st.info("Hint: Look for differences in the query structure, particularly added or removed terms.")