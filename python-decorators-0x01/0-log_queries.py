import sqlite3
import functools

def log_queries(func):
    """Decorator that logs SQL queries before execution"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Get query from either args or kwargs
        query = kwargs.get('query', args[0] if args else None)
        print(f"Executing query: {query}")
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

if __name__ == "__main__":
    users = fetch_all_users(query="SELECT * FROM users")
    print(users)