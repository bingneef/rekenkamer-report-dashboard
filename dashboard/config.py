import os

UTILITY_API_URL = os.getenv("UTILITY_API_URL", 'http://localhost:5000')
ENABLE_CUSTOM_SOURCE_CREATE = os.getenv("ENABLE_CUSTOM_SOURCE_CREATE", 0) == "1"
ENABLE_CUSTOM_SOURCE_DELETE = os.getenv("ENABLE_CUSTOM_SOURCE_DELETE", 0) == "1"
