import streamlit as st
import pandas as pd
import uuid
import datetime
import random
from components.sidebar import render_sidebar

# Initialize page
st.set_page_config(
    page_title="BDA Studio - Chat",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Render sidebar
render_sidebar()

# Check if user has selected a workspace and an assistant
if not st.session_state.current_workspace:
    st.warning("Please select or create a workspace first")
    st.stop()

if not st.session_state.current_assistant:
    st.warning("Please select an assistant to chat with")
    st.stop()

# Initialize chat history if not present
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# Function to generate mock SQL response
def generate_sql_response(query):
    """Mock function to generate SQL from natural language"""
    assistant = st.session_state.current_assistant
    dataset = assistant['dataset']
    
    # Get random table from the dataset
    if dataset['tables']:
        table = random.choice(dataset['tables'])
        table_name = table['name']
    else:
        table_name = "example_table"
    
    # Generate a simple SQL query based on the input
    if "count" in query.lower() or "how many" in query.lower():
        sql = f"SELECT COUNT(*) FROM `{dataset['project']}.{dataset['dataset']}.{table_name}`"
        if "where" in query.lower() or "filter" in query.lower():
            sql += " WHERE created_date > '2023-01-01'"
    elif "average" in query.lower() or "mean" in query.lower():
        sql = f"SELECT AVG(value) FROM `{dataset['project']}.{dataset['dataset']}.{table_name}`"
    elif "group" in query.lower():
        sql = f"SELECT category, COUNT(*) FROM `{dataset['project']}.{dataset['dataset']}.{table_name}` GROUP BY category"
    elif "top" in query.lower():
        sql = f"SELECT category, COUNT(*) as count FROM `{dataset['project']}.{dataset['dataset']}.{table_name}` GROUP BY category ORDER BY count DESC LIMIT 5"
    else:
        sql = f"SELECT * FROM `{dataset['project']}.{dataset['dataset']}.{table_name}` LIMIT 10"
    
    return sql

# Function to generate mock query results
def generate_query_results(sql):
    """Mock function to generate query results from SQL"""
    # Check the type of query to determine what kind of results to generate
    if "COUNT(*)" in sql:
        # Return a count result
        count = random.randint(100, 10000)
        return pd.DataFrame({"count": [count]})
    elif "AVG" in sql:
        # Return an average result
        avg_value = random.uniform(10, 1000)
        return pd.DataFrame({"average": [round(avg_value, 2)]})
    elif "GROUP BY" in sql:
        # Return grouped results
        categories = ["Category A", "Category B", "Category C", "Category D", "Category E"]
        counts = [random.randint(50, 500) for _ in range(len(categories))]
        return pd.DataFrame({"category": categories, "count": counts})
    else:
        # Return a table of results
        columns = ["id", "name", "category", "value", "created_date"]
        data = []
        for i in range(10):  # Generate 10 rows
            data.append({
                "id": i + 1,
                "name": f"Item {i+1}",
                "category": random.choice(["Category A", "Category B", "Category C"]),
                "value": round(random.uniform(10, 1000), 2),
                "created_date": f"2023-{random.randint(1,12):02d}-{random.randint(1,28):02d}"
            })
        return pd.DataFrame(data)

# Display assistant info in the header
assistant = st.session_state.current_assistant
version = st.session_state.current_assistant_version

st.title(f"Chat with {assistant['name']} (v{version})")

# Display assistant metadata
col1, col2, col3 = st.columns(3)
with col1:
    st.write(f"**Dataset:** {assistant['dataset']['project']}.{assistant['dataset']['dataset']}")
with col2:
    st.write(f"**Material:** {assistant['material']['name']}")
with col3:
    st.write(f"**Created:** {assistant['created_at']}")

# Chat container
st.divider()
chat_container = st.container()

# Display chat history
with chat_container:
    for message in st.session_state.chat_history:
        if message["role"] == "user":
            st.chat_message("user").write(message["content"])
        else:
            with st.chat_message("assistant"):
                st.write(message["content"])
                if "sql" in message:
                    st.code(message["sql"], language="sql")
                if "results" in message:
                    st.dataframe(message["results"])

# Chat input
prompt = st.chat_input("Ask a question in natural language...")

if prompt:
    # Add user message to chat history
    st.session_state.chat_history.append({"role": "user", "content": prompt})
    
    # Display user message
    st.chat_message("user").write(prompt)
    
    # Generate SQL (in a real app, this would call your LLM)
    sql = generate_sql_response(prompt)
    
    # Generate query results (in a real app, this would query BigQuery)
    results = generate_query_results(sql)
    
    # Create assistant response
    response = f"I've translated your question into SQL and executed it."
    
    # Add assistant message to chat history
    st.session_state.chat_history.append({
        "role": "assistant", 
        "content": response,
        "sql": sql,
        "results": results
    })
    
    # Display assistant message
    with st.chat_message("assistant"):
        st.write(response)
        st.code(sql, language="sql")
        st.dataframe(results)

# Clear chat button
if st.button("Clear Chat"):
    st.session_state.chat_history = []
    st.rerun()