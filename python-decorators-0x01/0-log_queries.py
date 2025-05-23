import sqlite3
import functools

def log_queries(func):
    """Decorator that logs SQL queries before execution"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Get the query from either args or kwargs
        query = kwargs.get('query') or (args[0] if args else None)
        
        # Log the query
        print(f"Executing query: {query}")
        
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

# Fetch users while logging the query
users = fetch_all_users(query="SELECT * FROM users")