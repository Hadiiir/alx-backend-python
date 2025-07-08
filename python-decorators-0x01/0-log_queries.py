import sqlite3
import functools
from datetime import datetime

#### decorator to log SQL queries

def log_queries(func):
    """
    Decorator that logs SQL queries before executing them.
    
    Args:
        func: Function that executes database queries
        
    Returns:
        Wrapped function that logs queries before execution
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Extract the query from function arguments
        # Assuming the query is passed as a keyword argument or first positional argument
        query = None
        
        # Check if query is in kwargs
        if 'query' in kwargs:
            query = kwargs['query']
        # Check if query is in args (assuming it's the first argument)
        elif args:
            query = args[0]
        
        # Log the query if found
        if query:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[{timestamp}] Executing SQL Query: {query}")
        
        # Execute the original function
        return func(*args, **kwargs)
    
    return wrapper

@log_queries
def fetch_all_users(query):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()
    return results

#### fetch users while logging the query
users = fetch_all_users(query="SELECT * FROM users")