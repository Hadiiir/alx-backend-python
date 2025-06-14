# Add this to your settings.py file
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}

# Optional: Add cache middleware for better performance
MIDDLEWARE = [
    # ... other middleware
    'django.middleware.cache.UpdateCacheMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.cache.FetchFromCacheMiddleware',
    # ... other middleware
]

# Cache timeout in seconds (optional)
CACHE_MIDDLEWARE_SECONDS = 60