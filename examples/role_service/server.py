import logging

from sanicms.server import app
from sanicms.client import Client

from views import role_bp

logger = logging.getLogger('sanic')

app.blueprint(role_bp)


@app.route('/')
async def index(request):
    return 'role service'


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=app.config['PORT'], debug=True)
