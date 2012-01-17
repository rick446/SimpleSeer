from base import *
from Session import *


atexit.register(cherrypy.engine.exit)

def jsonify(fn):
    def new(*args, **kwargs):
        cherrypy.response.headers['Content-Type'] = 'application/json'
        return jsonencode(fn(*args, **kwargs))
    return new

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
                'log.screen' : True,
                'tools.staticdir.on': True,
                'tools.staticdir.dir': os.getcwd() + "/public/",
                }
            }

    def __init__(self):
        cherrypy.tree.mount(WebInterface())
        cherrypy.config.update(self.config)
        cherrypy.engine.start()



    

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
    @jsonify
    def inspection_preview(self, **params):        
        insp = Inspection(
            name = params["name"],
            camera = params["camera"],
            method = params["method"],
            parameters = json.loads(params["parameters"]))
            #TODO fix for different cameras
            #TODO catch malformed data
        
        features = insp.execute(SimpleSeer.SimpleSeer().lastframes[-1][0].image)
        
        return { "inspection": insp, "features": features}

    @cherrypy.expose
    @jsonify
    def inspection_add(self, **params):        
        #try:
        Inspection(
            name = params["name"],
            camera = params["camera"],
            method = params["method"],
            parameters = json.loads(params["parameters"])).save()
        #except Exception as e:
        #    return dict( error = e )
        #TODO catch malformed data
        #TODO add parameters for morphs, parent etc
        SimpleSeer.SimpleSeer().reloadInspections()
        
        return SimpleSeer.SimpleSeer().inspections

    @cherrypy.expose
    @jsonify
    def inspection_remove(self, **params):
        Inspection.objects(id = bson.ObjectId(params["id"])).delete()
        SimpleSeer.SimpleSeer().reloadInspections()
        
        return SimpleSeer.SimpleSeer().inspections

    @cherrypy.expose
    @jsonify
    def poll(self):
        text = "Wow, this is some fun stuff"
        return {"text": text }


import SimpleSeer
from Inspection import Inspection
