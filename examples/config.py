import os

"""
Basic config
"""
DB_CONFIG = {
    'host':  os.environ.get('POSTGRES_SERVICE_HOST', 'localhost'),
    'user': os.environ.get('POSTGRES_SERVICE_USER', 'postgres'),
    'password': os.environ.get('POSTGRES_SERVICE_PASSWORD', None),
    'port': os.environ.get('POSTGRES_SERVICE_PORT', 5432),
    'database': os.environ.get('POSTGRES_SERVICE_DB_NAME', 'postgres')
}

ZIPKIN_SERVER = os.environ.get('ZIPKIN_SERVER', None)
ACCESS_CONTROL_ALLOW_ORIGIN = os.environ.get("ACCESS_CONTROL_ALLOW_ORIGIN", "")
ACCESS_CONTROL_ALLOW_HEADERS = os.environ.get("ACCESS_CONTROL_ALLOW_HEADERS", "")
ACCESS_CONTROL_ALLOW_METHODS = os.environ.get("ACCESS_CONTROL_ALLOW_METHODS", "")
