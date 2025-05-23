import sqlite3

class ExecuteQuery:
    def __init__(self, query, params=None):
        self.query = query
        self.params = params if params is not None else ()
        self.conn = None
        self.cursor = None
        self.results = None

    def __enter__(self):
        self.conn = sqlite3.connect('users.db')
        self.cursor = self.conn.cursor()
        self.cursor.execute(self.query, self.params)
        self.results = self.cursor.fetchall()
        return self.results

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        return False  # Propagate exceptions if any

# Using the context manager to perform a query
with ExecuteQuery("SELECT * FROM users WHERE age > ?", (25,)) as results:
    for row in results:
        print(row)