import os


APP_ID = 'region-service'

HOST = os.environ.get('SERVER_HOST', None)
PORT = os.environ.get('SERVER_PORT', 8050)

DB_CONFIG = {
    'host':  os.environ.get('POSTGRES_SERVICE_HOST', 'localhost'),
    'user': os.environ.get('POSTGRES_SERVICE_USER', 'postgres'),
    'password': os.environ.get('POSTGRES_SERVICE_PASSWORD', None),
    'port': os.environ.get('POSTGRES_SERVICE_PORT', 5432),
    'database': os.environ.get('POSTGRES_SERVICE_DB_NAME', 'postgres')
}

SWAGGER = {
    'version': '1.0.0',
    'title': 'REGION API',
    'description': 'REGION API',
    'terms_of_service': 'Use with caution!',
    'termsOfService': ['application/json'],
    'contact_email': 'it@example.cn'
}

ZIPKIN_SERVER = os.environ.get('ZIPKIN_SERVER', None)
ACCESS_CONTROL_ALLOW_ORIGIN = os.environ.get("ACCESS_CONTROL_ALLOW_ORIGIN", "")
ACCESS_CONTROL_ALLOW_HEADERS = os.environ.get("ACCESS_CONTROL_ALLOW_HEADERS", "")
ACCESS_CONTROL_ALLOW_METHODS = os.environ.get("ACCESS_CONTROL_ALLOW_METHODS", "")

CONSUL_AGENT_HOST = os.environ.get('CONSUL_AGENT_HOST', '127.0.0.1')
CONSUL_AGENT_PORT = os.environ.get('CONSUL_AGENT_PORT', 8500)