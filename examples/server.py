import logging

from views import user_bp

from sanicms.server import app

logger = logging.getLogger('sanic')

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

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=app.config['PORT'], debug=True)
