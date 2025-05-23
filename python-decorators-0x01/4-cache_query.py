import time
import sqlite3
import functools

query_cache = {}

def with_db_connection(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        conn = sqlite3.connect('users.db')
        try:
            if 'conn' not in kwargs and (not args or not isinstance(args[0], sqlite3.Connection)):
                kwargs['conn'] = conn
            result = func(*args, **kwargs)
            return result
        finally:
            conn.close()
    return wrapper

def cache_query(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        query = kwargs.get('query', None)
        if query is None and args:
            query = args[1] if len(args) > 1 else None
        if query is None:
            return func(*args, **kwargs)
        if query in query_cache:
            return query_cache[query]
        result = func(*args, **kwargs)
        query_cache[query] = result
        return result
    return wrapper

@with_db_connection
@cache_query
def fetch_users_with_cache(conn, query):
    cursor = conn.cursor()
    cursor.execute(query)
    return cursor.fetchall()

# First call will cache the result
users = fetch_users_with_cache(query="SELECT * FROM users")

# Second call will use the cached result
users_again = fetch_users_with_cache(query="SELECT * FROM users")