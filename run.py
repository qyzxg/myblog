from app import create_app
from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
app = create_app('default')

if __name__ == '__main__':
    app.jinja_env.cache = {}
    app.run(debug=False)
    # http_server = HTTPServer(WSGIContainer(app))
    # http_server.listen(5000)
    # IOLoop.instance().start()

