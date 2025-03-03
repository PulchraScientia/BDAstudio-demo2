import uuid
import random
import datetime
import pandas as pd

def generate_mock_datasets():
    """Generate mock datasets for demo purposes"""
    projects = ["my-gcp-project", "shared-analytics-project", "customer-insights"]
    
    datasets_by_project = {
        "my-gcp-project": ["sales_data", "product_data", "user_activity"],
        "shared-analytics-project": ["marketing_campaigns", "web_analytics", "social_media"],
        "customer-insights": ["customer_profiles", "user_journey", "feedback_data"]
    }
    
    tables_by_dataset = {
        "sales_data": [
            {"name": "transactions", "description": "Daily sales transactions", "rows": "1.2M", "last_updated": "2023-12-01"},
            {"name": "products", "description": "Product catalog", "rows": "5.3K", "last_updated": "2023-11-15"},
            {"name": "customers", "description": "Customer information", "rows": "2.1M", "last_updated": "2023-11-25"}
        ],
        "product_data": [
            {"name": "product_catalog", "description": "Complete product information", "rows": "15K", "last_updated": "2023-12-05"},
            {"name": "categories", "description": "Product categories", "rows": "42", "last_updated": "2023-10-20"},
            {"name": "inventory", "description": "Current inventory levels", "rows": "15K", "last_updated": "2023-12-15"}
        ],
        "user_activity": [
            {"name": "page_views", "description": "Website page view events", "rows": "25M", "last_updated": "2023-12-15"},
            {"name": "user_sessions", "description": "User session data", "rows": "4.2M", "last_updated": "2023-12-15"},
            {"name": "clicks", "description": "User click events", "rows": "18M", "last_updated": "2023-12-15"}
        ],
        "marketing_campaigns": [
            {"name": "campaigns", "description": "Marketing campaign details", "rows": "350", "last_updated": "2023-11-30"},
            {"name": "ad_performance", "description": "Ad performance metrics", "rows": "25K", "last_updated": "2023-12-10"},
            {"name": "campaign_spend", "description": "Campaign spending data", "rows": "1.2K", "last_updated": "2023-12-05"}
        ],
        "web_analytics": [
            {"name": "visits", "description": "Website visit data", "rows": "12M", "last_updated": "2023-12-15"},
            {"name": "conversions", "description": "Conversion events", "rows": "450K", "last_updated": "2023-12-15"},
            {"name": "referrers", "description": "Traffic referral sources", "rows": "280K", "last_updated": "2023-12-10"}
        ],
        "customer_profiles": [
            {"name": "customers", "description": "Customer profile information", "rows": "3.5M", "last_updated": "2023-12-01"},
            {"name": "segments", "description": "Customer segmentation", "rows": "25", "last_updated": "2023-11-20"},
            {"name": "preferences", "description": "Customer preferences", "rows": "5.8M", "last_updated": "2023-12-05"}
        ]
    }
    
    datasets = []
    
    for project in projects:
        for dataset_name in datasets_by_project[project]:
            if dataset_name in tables_by_dataset:
                dataset = {
                    "id": str(uuid.uuid4()),
                    "project": project,
                    "dataset": dataset_name,
                    "tables": tables_by_dataset[dataset_name],
                    "last_updated": datetime.datetime.now().strftime("%Y-%m-%d")
                }
                datasets.append(dataset)
    
    return datasets

def generate_mock_materials():
    """Generate mock materials for demo purposes"""
    materials = []
    
    # Sales data material
    sales_material = {
        "id": str(uuid.uuid4()),
        "name": "Sales Data Material",
        "training_set": [
            {"nl": "How many sales did we have yesterday?", "sql": "SELECT COUNT(*) FROM `sales_data.transactions` WHERE date = DATE_SUB(CURRENT_DATE(), INTERVAL 1 DAY)"},
            {"nl": "Show me top 5 products by revenue", "sql": "SELECT p.name, SUM(t.quantity * t.price) as revenue FROM `sales_data.transactions` t JOIN `sales_data.products` p ON t.product_id = p.id GROUP BY p.name ORDER BY revenue DESC LIMIT 5"},
            {"nl": "What's our total revenue this month?", "sql": "SELECT SUM(quantity * price) as revenue FROM `sales_data.transactions` WHERE DATE_TRUNC(date, MONTH) = DATE_TRUNC(CURRENT_DATE(), MONTH)"}
        ],
        "test_set": [
            {"nl": "Show me sales by product category", "sql": "SELECT p.category, SUM(t.quantity * t.price) as revenue FROM `sales_data.transactions` t JOIN `sales_data.products` p ON t.product_id = p.id GROUP BY p.category ORDER BY revenue DESC"},
            {"nl": "How many customers made a purchase last week?", "sql": "SELECT COUNT(DISTINCT customer_id) FROM `sales_data.transactions` WHERE date BETWEEN DATE_SUB(CURRENT_DATE(), INTERVAL 7 DAY) AND CURRENT_DATE()"},
            {"nl": "What's the average purchase value?", "sql": "SELECT AVG(quantity * price) as avg_purchase FROM `sales_data.transactions`"}
        ],
        "knowledge_data": "The sales_data dataset contains transaction records, product information, and customer data. Transactions have fields: id, customer_id, product_id, quantity, price, date. Products have fields: id, name, category, cost, price. Customers have fields: id, name, email, registration_date.",
        "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    materials.append(sales_material)
    
    # Web analytics material
    web_material = {
        "id": str(uuid.uuid4()),
        "name": "Web Analytics Material",
        "training_set": [
            {"nl": "What's our daily website traffic for the past week?", "sql": "SELECT date, COUNT(*) as visits FROM `web_analytics.visits` WHERE date BETWEEN DATE_SUB(CURRENT_DATE(), INTERVAL 7 DAY) AND CURRENT_DATE() GROUP BY date ORDER BY date"},
            {"nl": "Show me conversion rate by traffic source", "sql": "SELECT v.referrer, COUNT(DISTINCT c.visitor_id) / COUNT(DISTINCT v.visitor_id) * 100 as conversion_rate FROM `web_analytics.visits` v LEFT JOIN `web_analytics.conversions` c ON v.visitor_id = c.visitor_id GROUP BY v.referrer ORDER BY conversion_rate DESC"},
            {"nl": "Which pages have the highest bounce rate?", "sql": "SELECT page_url, COUNT(CASE WHEN session_duration < 10 THEN 1 END) / COUNT(*) * 100 as bounce_rate FROM `web_analytics.visits` GROUP BY page_url ORDER BY bounce_rate DESC LIMIT 10"}
        ],
        "test_set": [
            {"nl": "What percentage of users convert on first visit?", "sql": "SELECT COUNT(DISTINCT c.visitor_id) / COUNT(DISTINCT v.visitor_id) * 100 as first_visit_conversion FROM `web_analytics.visits` v LEFT JOIN `web_analytics.conversions` c ON v.visitor_id = c.visitor_id AND v.visit_number = 1"},
            {"nl": "Show me top 10 referrers by visit count", "sql": "SELECT referrer, COUNT(*) as visit_count FROM `web_analytics.visits` GROUP BY referrer ORDER BY visit_count DESC LIMIT 10"},
            {"nl": "What's our mobile vs desktop traffic ratio?", "sql": "SELECT device_type, COUNT(*) as visits, COUNT(*) / (SELECT COUNT(*) FROM `web_analytics.visits`) * 100 as percentage FROM `web_analytics.visits` GROUP BY device_type"}
        ],
        "knowledge_data": "The web_analytics dataset has three main tables: visits, conversions, and referrers. Visits contain visitor_id, session_id, page_url, date, time, device_type, referrer, visit_number, and session_duration. Conversions contain visitor_id, session_id, conversion_type, value, and timestamp. Referrers contain referrer_url, referrer_type, and referrer_domain.",
        "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    materials.append(web_material)
    
    # Customer data material
    customer_material = {
        "id": str(uuid.uuid4()),
        "name": "Customer Data Material",
        "training_set": [
            {"nl": "How many customers are in each segment?", "sql": "SELECT s.segment_name, COUNT(c.customer_id) as customer_count FROM `customer_profiles.customers` c JOIN `customer_profiles.segments` s ON c.segment_id = s.segment_id GROUP BY s.segment_name ORDER BY customer_count DESC"},
            {"nl": "What are the most common customer preferences?", "sql": "SELECT preference_type, COUNT(*) as preference_count FROM `customer_profiles.preferences` GROUP BY preference_type ORDER BY preference_count DESC LIMIT 5"},
            {"nl": "Show me average customer lifetime value by segment", "sql": "SELECT s.segment_name, AVG(c.lifetime_value) as avg_ltv FROM `customer_profiles.customers` c JOIN `customer_profiles.segments` s ON c.segment_id = s.segment_id GROUP BY s.segment_name ORDER BY avg_ltv DESC"}
        ],
        "test_set": [
            {"nl": "Which customers have not made a purchase in the last 90 days?", "sql": "SELECT customer_id, name, email FROM `customer_profiles.customers` WHERE last_purchase_date < DATE_SUB(CURRENT_DATE(), INTERVAL 90 DAY)"},
            {"nl": "What percentage of customers prefer email communication?", "sql": "SELECT COUNT(CASE WHEN preference_type = 'email' THEN 1 END) / COUNT(DISTINCT customer_id) * 100 as email_preference_percentage FROM `customer_profiles.preferences`"},
            {"nl": "Show me customers who signed up this month", "sql": "SELECT customer_id, name, email, signup_date FROM `customer_profiles.customers` WHERE DATE_TRUNC(signup_date, MONTH) = DATE_TRUNC(CURRENT_DATE(), MONTH)"}
        ],
        "knowledge_data": "The customer_profiles dataset contains customer information, segmentation, and preferences. Customers have fields: customer_id, name, email, phone, address, signup_date, last_purchase_date, lifetime_value, segment_id. Segments have fields: segment_id, segment_name, segment_description. Preferences have fields: preference_id, customer_id, preference_type, preference_value.",
        "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    materials.append(customer_material)
    
    return materials

def generate_mock_query_results(query_type="table"):
    """Generate mock query results based on query type"""
    if query_type == "count":
        # Return a count result
        count = random.randint(100, 10000)
        return pd.DataFrame({"count": [count]})
    
    elif query_type == "average":
        # Return an average result
        avg_value = random.uniform(10, 1000)
        return pd.DataFrame({"average": [round(avg_value, 2)]})
    
    elif query_type == "grouped":
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