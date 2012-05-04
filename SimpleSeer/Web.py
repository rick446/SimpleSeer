import os

import gevent
from gevent_zeromq import zmq
from flask import Flask
from socketio.server import SocketIOServer

from . import views
from . import realtime
from . import crud
from .Session import Session

DEBUG = True

def make_app():
    app = Flask(__name__)
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
        context = zmq.Context()
        def data_gen():
            cm = realtime.ChannelManager(context)
            while True:
                gevent.sleep(1)
                cm.publish('foo', dict(u='data', m='tick'))
        gevent.spawn(data_gen)
        server = SocketIOServer(
            (self.host, self.port),
            self.app, namespace='socket.io',
            policy_server=False)
        server.serve_forever()
        

