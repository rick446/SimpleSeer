from base import *
from Session import *


#atexit.register(cherrypy.engine.exit)


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
                'log.access_file' : "seer.access_log",
                'log.error_file' : "seer.error_log",
                'log.screen' : False,
                'tools.staticdir.on': True,
                'tools.staticdir.dir': os.getcwd() + "/public/",
                }
            }

    def __init__(self):
        log("web service started")
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
        
        return { "inspection": insp, "features": features }

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
        Inspection.inspect()
        SimpleSeer.SimpleSeer().update()
        
        return SimpleSeer.SimpleSeer().inspections

    @cherrypy.expose
    @jsonify
    def inspection_remove(self, **params):
        Inspection.objects(id = bson.ObjectId(params["id"])).delete()
        Measurement.objects(inspection = bson.ObjectId(params["id"])).delete()
        Result.objects(inspection = bson.ObjectId(params["id"])).delete()
        SimpleSeer.SimpleSeer().reloadInspections()
        Inspection.inspect()
        SimpleSeer.SimpleSeer().update()
        
        
        return SimpleSeer.SimpleSeer().inspections

    @cherrypy.expose
    @jsonify
    def frame_capture(self, **params):
        Frame.capture()
        Inspection.inspect()
        SimpleSeer.SimpleSeer().update()
        return dict( capture = "ok" )
        
    @cherrypy.expose
    @jsonify
    def frame_inspect(self, **params):
        Inspection.inspect()
        SimpleSeer.SimpleSeer().update()
        return dict( inspect = "ok" )    
    
    @cherrypy.expose
    @jsonify
    def measurement_add(self, **params):
        if not params.has_key('units'):
            params['units'] = 'px';
        
        m = Measurement(name = params["name"],
            label = params['label'],
            method = params['method'],
            featurecriteria = json.loads(params["featurecriteria"]),
            parameters = json.loads(params["parameters"]),
            units = params['units'],
            inspection = bson.ObjectId(params['inspection']))
        m.save()
        
        #backfill?
        
        SimpleSeer.SimpleSeer().reloadInspections()
        Inspection.inspect()
        SimpleSeer.SimpleSeer().update()
        
        return jsonencode(m)
    
    @cherrypy.expose
    @jsonify
    def measurement_remove(self, **params):
        Measurement.objects(id = bson.ObjectId(params["id"])).delete()
        Result.objects(measurement = bson.ObjectId(params["id"])).delete()
        
        SimpleSeer.SimpleSeer().reloadInspections()
        SimpleSeer.SimpleSeer().update()

        return dict( remove = "ok")
    
    @cherrypy.expose
    @jsonify
    def measurement_results(self, **params):
        return list(Result.objects(measurement = bson.ObjectId(params["id"])).order_by("-capturetime"))
    
    @cherrypy.expose
    @jsonify
    def ping(self):
        text = "pong"
        return {"text": text }


import SimpleSeer
from Inspection import Inspection
from Measurement import Measurement
from Result import Result
from Frame import Frame
