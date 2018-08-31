import logging

from sanicms.server import app
from sanicms.client import Client

from views import region_bp

logger = logging.getLogger('sanic')

app.blueprint(region_bp)


@app.route('/')
async def index(request):
    return 'region service'


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=app.config['PORT'], debug=True)
