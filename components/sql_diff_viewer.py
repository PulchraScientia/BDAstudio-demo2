import streamlit as st
import difflib
import html

def render_sql_diff(expected_sql, generated_sql):
    """
    Render a visual diff between expected and generated SQL queries
    
    Args:
        expected_sql (str): The expected/correct SQL query
        generated_sql (str): The generated SQL query to compare
    """
    st.subheader("SQL Comparison")
    
    # Display the raw queries side by side
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Expected SQL**")
        st.code(expected_sql, language="sql")
    
    with col2:
        st.markdown("**Generated SQL**")
        st.code(generated_sql, language="sql")
    
    # Check if they are different
    if expected_sql != generated_sql:
        st.subheader("Differences")
        
        # Generate a line-by-line diff
        diff = difflib.ndiff(expected_sql.splitlines(), generated_sql.splitlines())
        
        # Format the diff for display
        diff_output = []
        for line in diff:
            if line.startswith('+ '):
                # Added in generated SQL
                diff_output.append(f"<span style='color:green; background-color:#e6ffe6'>{html.escape(line)}</span>")
            elif line.startswith('- '):
                # Removed from expected SQL
                diff_output.append(f"<span style='color:red; background-color:#ffe6e6'>{html.escape(line)}</span>")
            elif line.startswith('? '):
                # Indicating where changes are within a line
                diff_output.append(f"<span style='color:blue; font-style:italic'>{html.escape(line)}</span>")
            else:
                # Unchanged
                diff_output.append(html.escape(line))
        
        # Display the formatted diff
        st.markdown(
            f"<pre style='white-space: pre-wrap;'>{'<br>'.join(diff_output)}</pre>", 
            unsafe_allow_html=True
        )
        
        # Generate a word-level diff for more detailed comparison
        st.subheader("Word-level Differences")
        
        # Tokenize SQL into words (this is a simplified approach)
        def tokenize_sql(sql):
            # Replace some SQL symbols with spaces to make them separate tokens
            for symbol in ['(', ')', ',', '.', '=', '<', '>', '+', '-', '*', '/', ';']:
                sql = sql.replace(symbol, f' {symbol} ')
            # Split by whitespace
            return [word for word in sql.split() if word.strip()]
        
        expected_tokens = tokenize_sql(expected_sql)
        generated_tokens = tokenize_sql(generated_sql)
        
        # Generate sequence matcher
        matcher = difflib.SequenceMatcher(None, expected_tokens, generated_tokens)
        
        # Format the diff for display
        diff_blocks = []
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == 'equal':
                # Unchanged blocks
                diff_blocks.append(' '.join(expected_tokens[i1:i2]))
            elif tag == 'replace':
                # Changed blocks
                diff_blocks.append(f"<span style='color:red; background-color:#ffe6e6'>-{' '.join(expected_tokens[i1:i2])}</span>")
                diff_blocks.append(f"<span style='color:green; background-color:#e6ffe6'>+{' '.join(generated_tokens[j1:j2])}</span>")
            elif tag == 'delete':
                # Deleted blocks
                diff_blocks.append(f"<span style='color:red; background-color:#ffe6e6'>-{' '.join(expected_tokens[i1:i2])}</span>")
            elif tag == 'insert':
                # Inserted blocks
                diff_blocks.append(f"<span style='color:green; background-color:#e6ffe6'>+{' '.join(generated_tokens[j1:j2])}</span>")
        
        # Display the formatted word-level diff
        st.markdown(
            f"<div style='white-space: pre-wrap; line-height: 1.5; font-family: monospace;'>{'<br>'.join(diff_blocks)}</div>", 
            unsafe_allow_html=True
        )
    else:
        st.success("The SQL queries are identical!")