import os

from flask import Flask
from socketio.server import SocketIOServer

from . import api
from .Session import Session

DEBUG = True

def make_app():
    from . import views
    app = Flask(__name__)
    for func, path, kwargs in views.routes:
        app.route(path, **kwargs)(func)
    api.register(app)
    return app

class WebServer(object):
    """
    This is the abstract web interface to handle event callbacks for Seer
    all it does is basically fire up a webserver on port 53317 to allow you
    to start interacting with Seer via a web interface
    """
    
    web_interface = None
    port = 8000 
    
    def __init__(self, app):
        self.app = app
        if app.config['DEBUG'] or DEBUG:
            from werkzeug import SharedDataMiddleware
            app.wsgi_app = SharedDataMiddleware(app.wsgi_app, {
              '/': os.path.join(os.path.dirname(__file__), 'static/public')
            })
        
        hostport = Session().web["address"].split(":")
        if len(hostport) == 2:
            host, port = hostport
            port = int(port)
        else:
            host, port = hostport, 80
        self.host, self.port = host, port

    def __call__(self, environ, start_response):
        if environ['PATH_INFO'].startswith('/socket.io'):
            socket = environ['socketio']
            return self.handle_socket_io(socket)
        return self.app(environ, start_response)

    def handle_socket_io(self, socket):
        pass
        
    def run_flask_server(self):
        self.app.run(host=self.host, port=self.port)

    def start_gevent_server(self):
        return SocketIOServer(
            (self.host, self.port),
            self, resource='socket.io')
        
