from base import *

class Web():
    """
    This is the abstract web interface to handle event callbacks for Seer
    all it does is basically fire up a webserver on port 53317 to allow you
    to start interacting with Seer via a web interface
    """
    config =  { 'global' :
                {
                'server.socket_port': 53317,
                'server.socket_host' : '0.0.0.0',
                'log.screen' : False,
                'tools.staticdir.on': True,
                'tools.staticdir.dir': os.getcwd() + "/public/"
                }
            }

    def __init__(self):
        cherrypy.tree.mount(WebInterface())
        cherrypy.config.update(self.config)
        cherrypy.engine.start()
        atexit.register(cherrypy.engine.exit)


    

class WebInterface(object):
    """
    This is where all the event call backs and data handling happen for the
    internal webserver for Seer
    """

    @cherrypy.expose
    def index(self):
        filename = "index.html"
        subdirectory = "public"
        f = urllib.urlopen(subdirectory + "/" + filename)
        s = f.read() # read the file
        f.close()
        return s


    @cherrypy.expose
    def options(self):
        filename = "options.html"
        subdirectory = "public"
        f = urllib.urlopen(subdirectory + "/" + filename)
        s = f.read() # read the file
        f.close()
        return s

    @cherrypy.expose
    def modal(self):
        filename = "modal.html"
        subdirectory = "public"
        f = urllib.urlopen(subdirectory + "/" + filename)
        s = f.read() # read the file
        f.close()
        return s

    @cherrypy.expose
    def products(self):
        filename = "products.html"
        subdirectory = "public"
        f = urllib.urlopen(subdirectory + "/" + filename)
        s = f.read() # read the file
        f.close()
        return s


    

    
