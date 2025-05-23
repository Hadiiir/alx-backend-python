import sqlite3
import functools

def log_queries(func):
    """Decorator to log SQL queries before execution"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Get query from either kwargs or args
        query = kwargs.get('query', args[0] if args else None)
        print(f"Executing query: {query}")
        return func(*args, **kwargs)
    return wrapper

@log_queries
def fetch_all_users(query):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    # Create table if it doesn't exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            name TEXT,
            email TEXT
        )
    """)
    
    # Add sample data if empty
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO users (name, email) VALUES ('John Doe', 'john@example.com')")
        cursor.execute("INSERT INTO users (name, email) VALUES ('Jane Smith', 'jane@example.com')")
        conn.commit()
    
    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()
    return results

if __name__ == "__main__":
    users = fetch_all_users(query="SELECT * FROM users")
    print("Results:", users)