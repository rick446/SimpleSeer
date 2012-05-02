import os
import json

from flask import Flask, request
from socketio import socketio_manage
from socketio.server import SocketIOServer
from socketio.namespace import BaseNamespace

from . import crud
from . import models as M

DEBUG = True

def make_app():
    from . import views
    app = Flask(__name__)
    views.route.register_routes(app)
    crud.register(app)
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
        
        hostport = M.Session().web["address"].split(":")
        if len(hostport) == 2:
            host, port = hostport
            port = int(port)
        else:
            host, port = hostport, 80
        self.host, self.port = host, port

    def __call__(self, environ, start_response):
        if environ['PATH_INFO'].startswith('/socket.io'):
            socketio_manage(
                environ,
                {'/chat': ChatNamespace })
            return 'out'
        return self.app(environ, start_response)
        
    def run_flask_server(self):
        self.app.run(host=self.host, port=self.port)

    def run_gevent_server(self):
        server = SocketIOServer(
            (self.host, self.port),
            self, namespace='socket.io',
            policy_server=False)
        server.serve_forever()
        
class ChatNamespace(BaseNamespace):

    def on_chat(self, msg):
        self.emit('chat', json.dumps(dict(
                    u='user',
                    m='got your message %s'% msg)))
