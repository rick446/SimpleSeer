from base import *
from Session import *
from flask import Flask, jsonify, render_template, request
from werkzeug import SharedDataMiddleware

app = Flask(__name__)
#~ app.debug = True
DEBUG = True


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
        

		@app.route('/frame')
		@app.route('/frame/<int:index>')
		#~ @app.route('/frame')
		#~ @app.route('/login', methods=['GET', 'POST'])
		#~ def frame(self, index = -1, camera = 0, **params):
		def frame(index = -1):
				#~ searchword = request.args.get('q', '')
				camera = request.args.get('camera', '')
				print camera
				#~ print searchword
				index = -1
				s = StringIO()
				f = SimpleSeer.SimpleSeer().lastframes[index][0]

				try:
						f.image.getPIL().save(s, "webp", quality = 80)
						return s.getvalue()

				except:
						f.image.getPIL().save(s, "jpeg", quality = 80)
						return s.getvalue()


import SimpleSeer
from Inspection import Inspection
from Measurement import Measurement
from Result import Result
from Frame import Frame
from Watcher import Watcher
