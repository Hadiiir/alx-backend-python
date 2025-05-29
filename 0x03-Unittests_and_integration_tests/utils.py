#!/usr/bin/env python3
"""
Utility functions for testing
"""
import requests
from functools import wraps
from typing import Mapping, Sequence, Any, Dict, Callable


def access_nested_map(nested_map: Mapping, path: Sequence) -> Any:
    """
    Access a value in a nested dictionary using a sequence of keys.
    
    Args:
        nested_map: The nested dictionary
        path: Sequence of keys to access the value
        
    Returns:
        The accessed value
        
    Raises:
        KeyError: If the path is invalid
    """
    for key in path:
        if not isinstance(nested_map, Mapping):
            raise KeyError(key)
        nested_map = nested_map[key]
    return nested_map


def get_json(url: str) -> Dict:
    """
    Get JSON data from a URL.
    
    Args:
        url: The URL to fetch JSON from
        
    Returns:
        The JSON response as a dictionary
    """
    response = requests.get(url)
    return response.json()


def memoize(func: Callable) -> Callable:
    """
    Decorator to cache function results.
    
    Args:
        func: The function to memoize
        
    Returns:
        The memoized function
    """
    cache = {}

    @wraps(func)
    def memoized_func(*args):
        if args not in cache:
            cache[args] = func(*args)
        return cache[args]
    
    return memoized_func