import streamlit as st
import uuid
import datetime

def initialize_session_state():
    """Initialize the session state with default values if not already set"""
    
    # User information
    if 'user' not in st.session_state:
        st.session_state.user = {
            "name": "Demo User",
            "email": "demo@example.com",
            "role": "Data Analyst"
        }
    
    # Workspaces
    if 'workspaces' not in st.session_state:
        st.session_state.workspaces = []
        
    if 'current_workspace' not in st.session_state:
        st.session_state.current_workspace = None
    
    # Datasets
    if 'datasets' not in st.session_state:
        st.session_state.datasets = []
        
    if 'selected_dataset' not in st.session_state:
        st.session_state.selected_dataset = None
    
    # Materials
    if 'materials' not in st.session_state:
        st.session_state.materials = []
        
    if 'selected_material' not in st.session_state:
        st.session_state.selected_material = None
    
    # Experiments
    if 'experiments' not in st.session_state:
        st.session_state.experiments = []
        
    if 'current_experiment' not in st.session_state:
        st.session_state.current_experiment = None
    
    # Assistants
    if 'assistants' not in st.session_state:
        st.session_state.assistants = []
        
    if 'current_assistant' not in st.session_state:
        st.session_state.current_assistant = None
        
    if 'current_assistant_version' not in st.session_state:
        st.session_state.current_assistant_version = None
    
    # Chat
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []

def reset_session():
    """Reset the session state to defaults"""
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    initialize_session_state()

def add_demo_data():
    """Add demo data to the session state for testing"""
    # Demo workspace
    if not st.session_state.workspaces:
        workspace = {
            "id": str(uuid.uuid4()),
            "name": "Demo Workspace",
            "description": "A demo workspace for testing BDA Studio",
            "created_by": st.session_state.user["email"],
            "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        st.session_state.workspaces.append(workspace)
        st.session_state.current_workspace = workspace
    
    # Demo dataset
    if not st.session_state.datasets:
        dataset = {
            "id": str(uuid.uuid4()),
            "project": "demo-project",
            "dataset": "sales_data",
            "workspace_id": st.session_state.current_workspace["id"],
            "tables": [
                {"name": "transactions", "description": "Daily sales transactions", "rows": "1.2M", "last_updated": "2023-12-01"},
                {"name": "products", "description": "Product catalog", "rows": "5.3K", "last_updated": "2023-11-15"},
                {"name": "customers", "description": "Customer information", "rows": "2.1M", "last_updated": "2023-11-25"}
            ]
        }
        st.session_state.datasets.append(dataset)
        st.session_state.selected_dataset = dataset
    
    # Demo material
    if not st.session_state.materials:
        material = {
            "id": str(uuid.uuid4()),
            "name": "Sales Data Material",
            "workspace_id": st.session_state.current_workspace["id"],
            "training_set": [
                {"nl": "How many sales did we have yesterday?", "sql": "SELECT COUNT(*) FROM demo-project.sales_data.transactions WHERE date = DATE_SUB(CURRENT_DATE(), INTERVAL 1 DAY)"},
                {"nl": "Show me top 5 products by revenue", "sql": "SELECT p.name, SUM(t.quantity * t.price) as revenue FROM demo-project.sales_data.transactions t JOIN demo-project.sales_data.products p ON t.product_id = p.id GROUP BY p.name ORDER BY revenue DESC LIMIT 5"},
                {"nl": "What's our total revenue this month?", "sql": "SELECT SUM(quantity * price) as revenue FROM demo-project.sales_data.transactions WHERE DATE_TRUNC(date, MONTH) = DATE_TRUNC(CURRENT_DATE(), MONTH)"}
            ],
            "test_set": [
                {"nl": "Show me sales by product category", "sql": "SELECT p.category, SUM(t.quantity * t.price) as revenue FROM demo-project.sales_data.transactions t JOIN demo-project.sales_data.products p ON t.product_id = p.id GROUP BY p.category ORDER BY revenue DESC"},
                {"nl": "How many customers made a purchase last week?", "sql": "SELECT COUNT(DISTINCT customer_id) FROM demo-project.sales_data.transactions WHERE date BETWEEN DATE_SUB(CURRENT_DATE(), INTERVAL 7 DAY) AND CURRENT_DATE()"},
                {"nl": "What's the average purchase value?", "sql": "SELECT AVG(quantity * price) as avg_purchase FROM demo-project.sales_data.transactions"}
            ],
            "knowledge_data": "The sales_data dataset contains transaction records, product information, and customer data. Transactions have fields: id, customer_id, product_id, quantity, price, date. Products have fields: id, name, category, cost, price. Customers have fields: id, name, email, registration_date.",
            "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        st.session_state.materials.append(material)
        st.session_state.selected_material = material
    
    # Demo experiment
    if not st.session_state.experiments:
        experiment = {
            "id": str(uuid.uuid4()),
            "name": "Sales Query Experiment",
            "description": "Testing natural language to SQL conversion for sales data",
            "workspace_id": st.session_state.current_workspace["id"],
            "dataset_id": st.session_state.selected_dataset["id"],
            "dataset": st.session_state.selected_dataset,
            "material_id": st.session_state.selected_material["id"],
            "material": st.session_state.selected_material,
            "status": "completed",
            "results": {
                "accuracy": 0.85,
                "test_results": []
            },
            "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Generate test results
        for test_item in st.session_state.selected_material["test_set"]:
            is_correct = hash(test_item["nl"]) % 4 != 0  # 75% correct rate
            
            generated_sql = test_item["sql"]
            if not is_correct:
                # Slightly modify the SQL to simulate an error
                if "WHERE" in generated_sql:
                    generated_sql = generated_sql.replace("WHERE", "WHERE LOWER(")
                    if "=" in generated_sql:
                        parts = generated_sql.split("=", 1)
                        generated_sql = f"{parts[0]}) ={parts[1]}"
            
            experiment["results"]["test_results"].append({
                "nl": test_item["nl"],
                "expected_sql": test_item["sql"],
                "generated_sql": generated_sql,
                "is_correct": is_correct
            })
        
        st.session_state.experiments.append(experiment)
        st.session_state.current_experiment = experiment
    
    # Demo assistant
    if not st.session_state.assistants:
        assistant = {
            "id": str(uuid.uuid4()),
            "name": "Sales Data Assistant",
            "description": "Assistant for querying sales data with natural language",
            "workspace_id": st.session_state.current_workspace["id"],
            "experiment_id": st.session_state.current_experiment["id"],
            "dataset": st.session_state.selected_dataset,
            "material": st.session_state.selected_material,
            "version": 1,
            "status": "active",
            "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        st.session_state.assistants.append(assistant)
        st.session_state.current_assistant = assistant
        st.session_state.current_assistant_version = 1