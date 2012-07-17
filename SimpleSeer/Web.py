import os
import logging

import mongoengine
from flask import Flask
from socketio.server import SocketIOServer

from . import views
from . import crud
from . import util
from .Session import Session

DEBUG = True

log = logging.getLogger(__name__)

def make_app():
    app = Flask(__name__)

    @app.teardown_request
    def teardown_request(exception):
        conn = mongoengine.connection.get_connection()
        conn.end_request()

    views.route.register_routes(app)
    crud.register(app)
    return app

class WebServer(object):
    """
    This is the abstract web interface to handle event callbacks for Seer
    all it does is basically fire up a webserver to allow you
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

    def run_gevent_server(self):
        server = SocketIOServer(
            (self.host, self.port),
            self.app, namespace='socket.io',
            policy_server=False)
        log.info('Web server running on %s:%s', self.host, self.port)
        server.serve_forever()
        

