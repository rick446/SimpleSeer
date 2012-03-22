from base import *
from Session import *
from flask import Flask, render_template, request
from werkzeug import SharedDataMiddleware

app = Flask(__name__)
#~ app.debug = True
DEBUG = True

def jsonify(fn):
    def new(*args, **kwargs):
        return jsonencode(fn(*args, **kwargs))
    return new

class Web2():
		"""
		This is the abstract web interface to handle event callbacks for Seer
		all it does is basically fire up a webserver on port 53317 to allow you
		to start interacting with Seer via a web interface
		"""

		web_interface = None
		port = 53317

		def __init__(self):
			if app.config['DEBUG'] or DEBUG:
					from werkzeug import SharedDataMiddleware
					app.wsgi_app = SharedDataMiddleware(app.wsgi_app, {
						'/': os.path.join(os.path.dirname(__file__), 'static')
					})
			self.web_interface = WebInterface2()
			app.run(port=self.port)
			
		

class WebInterface2(object):
		"""
		This is where all the event call backs and data handling happen for the
		internal webserver for Seer
		"""
		@app.route('/')
		def index():
				return render_template('index.html')

		@app.route('/test')
		def test():
				return 'This is a test of the emergency broadcast system'

		@app.route('/test.json')
		@app.route('/_test')
		@jsonify
		def test_json():
				return 'This is a test of the emergency broadcast system'
        

		@app.route('/frame')
		def frame():
			params = {
					'index': -1,
					'camera': 0,
					}
			params.update(request.args)
			s = StringIO()
			f = SimpleSeer.SimpleSeer().lastframes[params['index']][params['camera']]

			try:
					f.image.getPIL().save(s, "webp", quality = 80)
					return s.getvalue()

			except:
					f.image.getPIL().save(s, "jpeg", quality = 80)
					return s.getvalue()

		@app.route('/frame_capture')
		@jsonify
		def frame_capture():
				Frame.capture()
				Inspection.inspect()
				SimpleSeer.SimpleSeer().update()
				return dict( capture = "ok" )

		@app.route('/frame_inspect')
		@jsonify
		def frame_inspect():
			try:
				params = dict(request.args)
				Inspection.inspect()
				SimpleSeer.SimpleSeer().update()
				inspect = "ok"

			except:
				inspect = "fail"
				
			finally:
				return dict( inspect )
				
		@app.route('/histogram')
		@jsonify
		def histogram():
			params = dict(bins = 50, channel = '', focus = "", camera = 0, index = -1, frameid = '')
			params.update(request.args)			

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


		@app.route('/inspection_add')
		@jsonify
		def inspection_add():
			params = dict(request.args)

			try:
				Inspection(
					name = params.get("name"),	
					camera = params.get("camera"),
					method = params.get("method"),
					parameters = json.loads(params.get("parameters"))).save()
				SimpleSeer.SimpleSeer().reloadInspections()
				Inspection.inspect()
				SimpleSeer.SimpleSeer().update()
				return SimpleSeer.SimpleSeer().inspections
				
			except:
				return dict()
			
			
				
#~ 
		#~ @app.route('/inspection_preview')
		#~ @jsonify
		#~ def inspection_preview():
			#~ params = dict(request.args)
			#~ insp = Inspection(
				#~ name = params["name"],
				#~ camera = params["camera"],
				#~ method = params["method"],
				#~ parameters = json.loads(params["parameters"]))
				#~ #TODO fix for different cameras
				#~ #TODO catch malformed data
			#~ 
			#~ features = insp.execute(SimpleSeer.SimpleSeer().lastframes[-1][0].image)
			#~ 
			#~ return { "inspection": insp, "features": features }
#~ 
		#~ @app.route('/inspection_remove')
		#~ @jsonify
		#~ def inspection_remove():
			#~ params = dict(request.args)
			#~ Inspection.objects(id = bson.ObjectId(params["id"])).delete()
			#~ #for m in Measurement.objects(inspection = bson.ObjectId(params["id"])):
			#~ Watcher.objects.delete() #todo narrow by measurement
#~ 
			#~ Measurement.objects(inspection = bson.ObjectId(params["id"])).delete()
			#~ Result.objects(inspection = bson.ObjectId(params["id"])).delete()
			#~ SimpleSeer.SimpleSeer().reloadInspections()
			#~ Inspection.inspect()
			#~ SimpleSeer.SimpleSeer().update()
			#~ 
			#~ 
			#~ return SimpleSeer.SimpleSeer().inspections
#~ 
		#~ @app.route('/inspection_update')
		#~ @jsonify
		#~ def inspection_update():
			#~ params = dict(request.args)
			#~ results = Inspection.objects(id = bson.ObjectId(params["id"]))
			#~ if not len(results):
				#~ return { "error": "no inspection id"}
			#~ 
			#~ insp = results[0]
			#~ 
			#~ if params.has_key("name"):
				#~ insp.name = params["name"]
				#~ 
			#~ if params.has_key("parameters"):
				#~ insp.parameters = json.loads(params["parameters"])
				#~ 
			#~ #TODO, add sorts, filters etc
			#~ insp.save()
			#~ return SimpleSeer.SimpleSeer().inspections
#~ 
		#~ @app.route('/measurement_add')
		#~ @jsonify
		#~ def measurement_add():
			#~ params = dict(request.args)
			#~ if not params.has_key('units'):
				#~ params['units'] = 'px';
			#~ 
			#~ m = Measurement(name = params["name"],
				#~ label = params['label'],
				#~ method = params['method'],
				#~ featurecriteria = json.loads(params["featurecriteria"]),
				#~ parameters = json.loads(params["parameters"]),
				#~ units = params['units'],
				#~ inspection = bson.ObjectId(params['inspection']))
			#~ m.save()
			#~ 
			#~ #backfill?
			#~ 
			#~ SimpleSeer.SimpleSeer().reloadInspections()
			#~ Inspection.inspect()
			#~ SimpleSeer.SimpleSeer().update()
			#~ 
			#~ return jsonencode(m)
#~ 
		#~ @app.route('/measurement_remove')
		#~ @jsonify
		#~ def measurement_remove():
			#~ params = dict(request.args)
			#~ Measurement.objects(id = bson.ObjectId(params["id"])).delete()
			#~ Result.objects(measurement = bson.ObjectId(params["id"])).delete()
			#~ Watcher.objects.delete() #todo narrow by measurement
			#~ 
			#~ SimpleSeer.SimpleSeer().reloadInspections()
			#~ SimpleSeer.SimpleSeer().update()
#~ 
			#~ return dict( remove = "ok")
#~ 
		#~ @app.route('/measurement_results')
		#~ @jsonify
		#~ def measurement_results(self, **params):
			#~ params = dict(request.args)
			#~ return list(Result.objects(measurement = bson.ObjectId(params["id"])).order_by("-capturetime"))
#~ 
		#~ @app.route('/ping')
		#~ @jsonify
		#~ def ping():
			#~ text = "pong"
			#~ return {"text": text }
#~ 
#~ 
		#~ @app.route('/plugin_js')
		#~ def plugin_js():
			#~ params = dict(request.args)
			#~ 
			#~ js = ''
			#~ for plugin in SimpleSeer.SimpleSeer().plugins.keys():
				#~ path = SimpleSeer.SimpleSeer().pluginpath + "/" + plugin
				#~ js += "//SimpleSeer plugin " + plugin + "\n\n"
				#~ for f in [file for file in os.listdir(path) if re.search("js$", file)]:
					#~ js += open(path + "/" + f).read()
			#~ js += "\n\n\n";
			#~ return js
#~ 
		#~ @app.route('/start')
		#~ def start():
			#~ try:
				#~ SimpleSeer.SimpleSeer().start()
			#~ except:
				#~ SimpleSeer.SimpleSeer().resume()
			#~ return "OK"
#~ 
		#~ @app.route('/stop')
		#~ def stop():
			#~ SimpleSeer.SimpleSeer().stop()
			#~ return "OK"
#~ 
		#~ @app.route('/watcher_add')
		#~ @jsonify   
		#~ def watcher_add():
			#~ params = dict(request.args)
			#~ Watcher(**params).save()
			#~ 
			#~ SimpleSeer.SimpleSeer().reloadInspections()
			#~ return SimpleSeer.SimpleSeer().watchers
#~ 
		#~ @app.route('/watcher_list_handlers')
		#~ @jsonify
		#~ def watcher_list_handlers():
			#~ return [s for s in dir(Watcher) if re.match("handler_", s)]

		#~ @app.route('/watch_remove')
		#~ @jsonify    
		#~ def watcher_remove():
			#~ params = dict(request.args)
			#~ Watcher.objects(id = bson.ObjectId(params["id"])).delete()
			#~ 
			#~ SimpleSeer.SimpleSeer().reloadInspections()
			#~ return SimpleSeer.SimpleSeer().watchers
        #~ 
import SimpleSeer
from Inspection import Inspection
from Measurement import Measurement
from Result import Result
from Frame import Frame
from Watcher import Watcher
