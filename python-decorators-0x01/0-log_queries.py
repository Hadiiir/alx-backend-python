import sqlite3
import functools

def log_queries(func):
    """Decorator that logs SQL queries before execution"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Get query from either args or kwargs
        query = kwargs.get('query', None)
        if query is None and args:
            query = args[0]
        
        # Log the query
        print(f"Query: {query}")
        
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

# Example usage
if __name__ == "__main__":
    users = fetch_all_users(query="SELECT * FROM users")