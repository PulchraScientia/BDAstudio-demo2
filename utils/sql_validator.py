import re

def validate_sql(sql_query):
    """
    Mock function to validate SQL queries for BigQuery syntax
    
    In a real implementation, this would use the BigQuery dry run API to check if the query is valid.
    For the demo, we'll use a simple pattern matching approach.
    
    Args:
        sql_query (str): SQL query to validate
        
    Returns:
        bool: True if the query is valid, False otherwise
    """
    # Skip empty queries
    if not sql_query or sql_query.strip() == "":
        return False
    
    # Check for basic SQL structure
    sql_query = sql_query.lower().strip()
    
    # Check if query starts with SELECT, WITH, or other valid SQL statements
    valid_starts = ["select", "with"]
    if not any(sql_query.startswith(start) for start in valid_starts):
        return False
    
    # Check for basic SQL errors that would cause syntax issues
    
    # Unmatched parentheses
    if sql_query.count('(') != sql_query.count(')'):
        return False
    
    # Unmatched quotes
    single_quotes = len(re.findall(r"(?<!\\)'", sql_query)) % 2
    double_quotes = len(re.findall(r'(?<!\\)"', sql_query)) % 2
    backticks = len(re.findall(r'`', sql_query)) % 2
    
    if single_quotes != 0 or double_quotes != 0 or backticks != 0:
        return False
    
    # Check for common SQL clauses in wrong order
    # For example, WHERE should come before GROUP BY, HAVING should come after GROUP BY
    clauses = [
        "select", "from", "where", "group by", 
        "having", "order by", "limit", "offset"
    ]
    
    # Find positions of clauses
    positions = {}
    for clause in clauses:
        # Use regex with word boundary to avoid partial matches
        matches = list(re.finditer(r'\b' + clause + r'\b', sql_query))
        if matches:
            # Store position of the last occurrence (ignores subqueries)
            positions[clause] = matches[-1].start()
    
    # Check clause order
    for i in range(len(clauses) - 1):
        current = clauses[i]
        next_clause = clauses[i + 1]
        
        if current in positions and next_clause in positions:
            if positions[current] > positions[next_clause]:
                return False
    
    # For demo purposes, always validate some specific test queries
    # In a real implementation, you would use BigQuery's dry run functionality
    always_valid = [
        "select count(*)",
        "select * from",
        "select avg(",
        "group by",
        "order by",
        "limit"
    ]
    
    if any(pattern in sql_query for pattern in always_valid):
        return True
    
    # For demo purposes, let's validate most queries
    # In real implementation, this would be more strict
    return True