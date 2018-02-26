import logging

from views import user_bp

from sanicms.server import app

logger = logging.getLogger('sanic')

app.name = 'user-service'
# add blueprint
app.blueprint(user_bp)

#  @app.listener('before_server_start')
#  async def before_srver_start(app, loop):
#      app.client =  Client(loop, url=USER)
#
#  @app.listener('before_server_stop')
#  async def before_server_stop(app, loop):
#      app.client.close()

@app.route("/")
async def index(request):
    return 'Hello world'

app.config.API_VERSION = '1.0.0'
app.config.API_TITLE = 'USER API'
app.config.API_DESCRIPTION = 'USER API'
app.config.API_TERMS_OF_SERVICE = 'Use with caution!'
app.config.API_PRODUCES_CONTENT_TYPES = ['application/json']
app.config.API_CONTACT_EMAIL = 'it@example.cn'


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8010, debug=True)
