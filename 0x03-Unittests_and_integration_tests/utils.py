"""Utility functions for testing examples"""

def access_nested_map(nested_map, path):
    """
    Access a nested map with a sequence of keys.
    
    Args:
        nested_map: A nested dictionary
        path: A sequence of keys to access the nested value
        
    Returns:
        The value at the nested path
        
    Raises:
        KeyError: If any key in the path doesn't exist
    """
    result = nested_map
    for key in path:
        result = result[key]
    return result


def get_json(url):
    """
    Get JSON data from a URL.
    
    Args:
        url: The URL to fetch JSON from
        
    Returns:
        The JSON response as a dictionary
    """
    import requests
    response = requests.get(url)
    return response.json()


def memoize(func):
    """
    Memoization decorator that caches function results.
    
    Args:
        func: The function to memoize
        
    Returns:
        The memoized function
    """
    cache = {}
    
    def wrapper(*args, **kwargs):
        key = str(args) + str(sorted(kwargs.items()))
        if key not in cache:
            cache[key] = func(*args, **kwargs)
        return cache[key]
    
    return wrapper


# Example usage and testing
if __name__ == "__main__":
    # Test access_nested_map
    print("Testing access_nested_map:")
    
    # Test case 1
    nested_map1 = {"a": 1}
    path1 = ("a",)
    result1 = access_nested_map(nested_map1, path1)
    print(f"access_nested_map({nested_map1}, {path1}) = {result1}")
    
    # Test case 2
    nested_map2 = {"a": {"b": 2}}
    path2 = ("a",)
    result2 = access_nested_map(nested_map2, path2)
    print(f"access_nested_map({nested_map2}, {path2}) = {result2}")
    
    # Test case 3
    nested_map3 = {"a": {"b": 2}}
    path3 = ("a", "b")
    result3 = access_nested_map(nested_map3, path3)
    print(f"access_nested_map({nested_map3}, {path3}) = {result3}")
    
    # Test error cases
    print("\nTesting error cases:")
    try:
        access_nested_map({}, ("a",))
    except KeyError as e:
        print(f"KeyError for empty dict: {e}")
    
    try:
        access_nested_map({"a": 1}, ("a", "b"))
    except KeyError as e:
        print(f"KeyError for invalid path: {e}")