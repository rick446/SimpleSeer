from base import *
from Session import *
from functools import wraps
from flask import Flask, render_template, request, make_response, Blueprint
from flask_rest import RESTResource
from werkzeug import SharedDataMiddleware

app = Flask(__name__)
#~ app.debug = True
DEBUG = True

restapi = Blueprint("restapi", __name__, url_prefix="")
from flask import Blueprint

class InspectionHandler(object):
    def add(self):
        print "Inspection Add " + str(request.values)
        return 201, "hi"
    
    def update(self, inspection_id):
        print "Inspection update " + str(request.values)
        return 200, "hi"
    
    def delete(self, inspection_id):
        print "Inspection delete " + str(request.values)
        return 200, "hi"
    
    def get(self, inspection_id):
        print "Inspection get " + str(request.values)
        return 200, "hi"
      
    def list(self):
        print "Inspection get list " + str(request.values)
        return 200, "hi"


inspection_api = RESTResource(
    name="inspection", # name of the var to inject to the methods
    route="/inspection",  # will be availble at /api/projects/*
    app=restapi, # the app which should handle this
    actions=["list", "add", "update", "delete", "get"], #authorised actions
    handler=InspectionHandler()) # the handler of the request


app.register_blueprint(restapi)

def jsonify(f):
    """
    We're going to use our own jsonify decorator, which uses our jsonencode function
    which routes thru json-pickle
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        obj = f(*args, **kwargs)
        if obj is None:
            obj = {}
            
        resp = make_response(jsonencode(obj), 200)
        resp.headers["Content-Type"] = 'application/json'
        return resp
    return decorated_function


class Web():
    """
    This is the abstract web interface to handle event callbacks for Seer
    all it does is basically fire up a webserver on port 53317 to allow you
    to start interacting with Seer via a web interface
    """
    
    web_interface = None
    port = 8000 
    
    def __init__(self):
        if app.config['DEBUG'] or DEBUG:
            from werkzeug import SharedDataMiddleware
            app.wsgi_app = SharedDataMiddleware(app.wsgi_app, {
              '/': os.path.join(os.path.dirname(__file__), 'static/public')
            })
        self.web_interface = WebInterface()
        
        port = 80
        hostport = Session().web["address"].split(":")
        if len(hostport) == 2:
            port = int(hostport[1])
        app.run(port=port)

        
class WebInterface(object):
    """
    This is where all the event call backs and data handling happen for the
    internal webserver for Seer
    """
    
    @app.route('/')
    def index():
        return open(os.path.join(os.path.dirname(__file__), 'static/public/index.html')).read()
    
    @app.route('/test', methods=['GET', 'POST'])
    def test():
        return 'This is a test of the emergency broadcast system'
    
    @app.route('/test.json', methods=['GET', 'POST'])
    @app.route('/_test', methods=['GET', 'POST'])

    def test_json():
      return 'This is a test of the emergency broadcast system'
        

    @app.route('/frame', methods=['GET', 'POST'])
    def frame():
        params = {
            'index': -1,
            'camera': 0,
            }
        params.update(request.values)
        s = StringIO()
        f = SimpleSeer.SimpleSeer().lastframes[params['index']][params['camera']]
    
        try:
            f.image.getPIL().save(s, "webp", quality = 80)
            resp = make_response(s.getvalue(), 200)
            resp.headers["Content-Type"] = "image/webp" 
            return resp
        except:
            f.image.getPIL().save(s, "jpeg", quality = 80)
            resp = make_response(s.getvalue(), 200)
            resp.headers["Content-Type"] = "image/jpeg" 
            return resp        


    @app.route('/frame_capture', methods=['GET', 'POST'])
    @jsonify
    def frame_capture():
        Frame.capture()
        Inspection.inspect()
        SimpleSeer.SimpleSeer().update()
        return dict( capture = "ok" )
    
    @app.route('/frame_inspect', methods=['GET', 'POST'])
    @jsonify
    def frame_inspect():
      try:
        params = request.values.to_dict()
        Inspection.inspect()
        SimpleSeer.SimpleSeer().update()
        return dict( inspect = "ok")
    
      except:
        return dict( inspect = "fail")
    
        
        
    @app.route('/histogram', methods=['GET', 'POST'])
    @jsonify
    def histogram():
      params = dict(bins = 50, channel = '', focus = "", camera = 0, index = -1, frameid = '')
      params.update(request.values.to_dict())			
    
      frame = SimpleSeer.SimpleSeer().lastframes[params['index']][params['camera']]
      focus = params['focus']
      if focus != "" and int(focus) < len(frame.features):
        feature = frame.features[int(focus)].feature
        feature.image = frame.image
        img = feature.crop()
      else:
        img = frame.image
    
      bins = params['bins']
      return img.histogram(bins)
    
    
    @app.route('/inspection_add', methods=['GET', 'POST'])
    @jsonify
    def inspection_add():
      params = request.values.to_dict()
    
      try:
        Inspection(
          name = params.get("name"),	
          camera = params.get("camera"),
          method = params.get("method"),
          parameters = json.loads(params.get("parameters"))).save()
        SimpleSeer.SimpleSeer().reloadInspections()
        Inspection.inspect()
        #SimpleSeer.SimpleSeer().update()
        return SimpleSeer.SimpleSeer().inspections
      except:
        return dict(status = "fail")
    
      
        
    
    @app.route('/inspection_preview', methods=['GET', 'POST'])
    @jsonify
    def inspection_preview():
      params = request.values.to_dict()
    
      try:
        insp = Inspection(
          name = params.get("name"),
          camera = params.get("camera"),
          method = params.get("method"),
          parameters = json.loads(params.get("parameters")))
          #TODO fix for different cameras
          #TODO catch malformed data
        features = insp.execute(SimpleSeer.SimpleSeer().lastframes[-1][0].image)
        return { "inspection": insp, "features": features }
      except:
        return dict(status = "fail")
      
      
    
    @app.route('/inspection_remove', methods=['GET', 'POST'])
    @jsonify
    def inspection_remove():
        params = request.values.to_dict()
        Inspection.objects(id = bson.ObjectId(params["id"])).delete()
        #for m in Measurement.objects(inspection = bson.ObjectId(params["id"])):
        Watcher.objects.delete() #todo narrow by measurement
    
        Measurement.objects(inspection = bson.ObjectId(params["id"])).delete()
        Result.objects(inspection = bson.ObjectId(params["id"])).delete()
        SimpleSeer.SimpleSeer().reloadInspections()
        Inspection.inspect()
        #SimpleSeer.SimpleSeer().update()
        
        
        return SimpleSeer.SimpleSeer().inspections
      #except:
      #  return dict(status = "fail")
    
    @app.route('/inspection_update', methods=['GET', 'POST'])
    @jsonify
    def inspection_update():
      try:
        params = request.values.to_dict()
        results = Inspection.objects(id = bson.ObjectId(params["id"]))
        if not len(results):
          return { "error": "no inspection id"}
        
        insp = results[0]
        
        if params.has_key("name"):
          insp.name = params["name"]
          
        if params.has_key("parameters"):
          insp.parameters = json.loads(params["parameters"])
          
        #TODO, add sorts, filters etc
        insp.save()
        return SimpleSeer.SimpleSeer().inspections
      except:
        return dict(status = "fail")
    
    @app.route('/measurement_add', methods=['GET', 'POST'])
    @jsonify
    def measurement_add():
      try:
        params = request.values.to_dict()
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
        #SimpleSeer.SimpleSeer().update()
        
        return m
      except:
        return dict(status = "fail")
    
    @app.route('/measurement_remove', methods=['GET', 'POST'])
    @jsonify
    def measurement_remove():
      try:
        params = request.values.to_dict()
        Measurement.objects(id = bson.ObjectId(params["id"])).delete()
        Result.objects(measurement = bson.ObjectId(params["id"])).delete()
        Watcher.objects.delete() #todo narrow by measurement
        
        SimpleSeer.SimpleSeer().reloadInspections()
        #SimpleSeer.SimpleSeer().update()
    
        return dict( remove = "ok")
      except:
        return dict(status = "fail")
    
    @app.route('/measurement_results', methods=['GET', 'POST'])
    @jsonify
    def measurement_results(self, **params):
      try:
        params = request.values.to_dict()
        return list(Result.objects(measurement = bson.ObjectId(params["id"])).order_by("-capturetime"))
      except:
        return dict(status = "fail")
        
    @app.route('/ping', methods=['GET', 'POST'])
    @jsonify
    def ping():
      text = "pong"
      return {"text": text }
    
    @app.route('/olap/<olap_name>', methods=['GET', 'POST'])
    @jsonify
    def olap(olap_name):
	  
	  o = OLAP.objects.get(_name = olap_name)
	  return o.createAll()
	  
    @app.route('/plugin_js', methods=['GET', 'POST'])
    def plugin_js():
      params = request.values.to_dict()
      
      js = ''
      for plugin in SimpleSeer.SimpleSeer().plugins.keys():
        path = SimpleSeer.SimpleSeer().pluginpath + "/" + plugin
        js += "//SimpleSeer plugin " + plugin + "\n\n"
        for f in [file for file in os.listdir(path) if re.search("js$", file)]:
          js += open(path + "/" + f).read()
      js += "\n\n\n";
      
      resp = make_response(js, 200)
      resp.headers['Content-Type'] = "application/javascript"
      return resp
    
    @app.route('/start', methods=['GET', 'POST'])
    def start():
      try:
        SimpleSeer.SimpleSeer().start()
      except:
        SimpleSeer.SimpleSeer().resume()
      return "OK"
    
    @app.route('/stop', methods=['GET', 'POST'])
    def stop():
      SimpleSeer.SimpleSeer().stop()
      return "OK"
    
    @app.route('/watcher_add', methods=['GET', 'POST'])
    @jsonify
    def watcher_add():
      params = request.values.to_dict()
      Watcher(**params).save()
      
      SimpleSeer.SimpleSeer().reloadInspections()
      return SimpleSeer.SimpleSeer().watchers
    
    @app.route('/watcher_list_handlers', methods=['GET', 'POST'])
    @jsonify
    def watcher_list_handlers():
      return [s for s in dir(Watcher) if re.match("handler_", s)]
    
    @app.route('/watch_remove', methods=['GET', 'POST'])
    @jsonify
    def watcher_remove():
      params = request.values.to_dict()
      Watcher.objects(id = bson.ObjectId(params["id"])).delete()
      
      SimpleSeer.SimpleSeer().reloadInspections()
      return SimpleSeer.SimpleSeer().watchers




import SimpleSeer
from Inspection import Inspection
from Measurement import Measurement
from Result import Result
from Frame import Frame
from Watcher import Watcher
from OLAP import OLAP, Query, Chart
