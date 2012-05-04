import os
import re
import json
from cStringIO import StringIO

import bson
from socketio import socketio_manage
from flask import request, make_response

from . import models as M
from . import util
from .realtime import RealtimeNamespace
from .service import SeerClient

class route(object):
    routes = []

    def __init__(self, path, **kwargs):
        self.path, self.kwargs = path, kwargs

    def __call__(self, func):
        self.routes.append(
            (func, self.path, self.kwargs))
        return func

    @classmethod
    def register_routes(cls, app):
        for func, path, kwargs in cls.routes:
            app.route(path, **kwargs)(func)

@route('/socket.io/<path:path>')
def sio(path):
    socketio_manage(
        request.environ,
        {'/rt': RealtimeNamespace },
        request._get_current_object())

@route('/')
def index():
    return open(os.path.join(
            os.path.dirname(__file__), 'static/public/index.html')).read()

@route('/test', methods=['GET', 'POST'])
def test():
    return 'This is a test of the emergency broadcast system'

@route('/test.json', methods=['GET', 'POST'])
@route('/_test', methods=['GET', 'POST'])

def test_json():
  return 'This is a test of the emergency broadcast system'


@route('/frame', methods=['GET', 'POST'])
def frame():
    params = {
        'index': -1,
        'camera': 0,
        }
    params.update(request.values)
    cli = SeerClient()
    result = cli.get_image(
        params['index'], params['camera'])
    resp = make_response(result['data'], 200)
    resp.headers['Content-Type'] = result['content_type']
    return resp


@route('/frame_capture', methods=['GET', 'POST'])
@util.jsonify
def frame_capture():
    M.Frame.capture()
    M.Inspection.inspect()
    util.get_seer().update()
    return dict( capture = "ok" )

@route('/frame_inspect', methods=['GET', 'POST'])
@util.jsonify
def frame_inspect():
  try:
    M.Inspection.inspect()
    util.get_seer().update()
    return dict( inspect = "ok")

  except:
    return dict( inspect = "fail")

@route('/histogram', methods=['GET', 'POST'])
@util.jsonify
def histogram():
  params = dict(bins = 50, channel = '', focus = "",
                camera = 0, index = -1, frameid = '')
  params.update(request.values.to_dict())			

  frame = (util.get_seer().lastframes
           [params['index']]
           [params['camera']])
  focus = params['focus']
  if focus != "" and int(focus) < len(frame.features):
    feature = frame.features[int(focus)].feature
    feature.image = frame.image
    img = feature.crop()
  else:
    img = frame.image

  bins = params['bins']
  return img.histogram(bins)


@route('/inspection_add', methods=['GET', 'POST'])
@util.jsonify
def inspection_add():
  params = request.values.to_dict()

  try:
    M.Inspection(
      name = params.get("name"),	
      camera = params.get("camera"),
      method = params.get("method"),
      parameters = json.loads(params.get("parameters"))).save()
    util.get_seer().reloadInspections()
    M.Inspection.inspect()
    #util.get_seer().update()
    return util.get_seer().inspections
  except:
    return dict(status = "fail")

@route('/inspection_preview', methods=['GET', 'POST'])
@util.jsonify
def inspection_preview():
  params = request.values.to_dict()
  try:
    insp = M.Inspection(
      name = params.get("name"),
      camera = params.get("camera"),
      method = params.get("method"),
      parameters = json.loads(params.get("parameters")))
      #TODO fix for different cameras
      #TODO catch malformed data
    features = insp.execute(util.get_seer().lastframes[-1][0].image)
    return { "inspection": insp, "features": features }
  except:
    return dict(status = "fail")



@route('/inspection_remove', methods=['GET', 'POST'])
@util.jsonify
def inspection_remove():
    params = request.values.to_dict()
    M.Inspection.objects(id = bson.ObjectId(params["id"])).delete()
    #for m in Measurement.objects(inspection = bson.ObjectId(params["id"])):
    M.Watcher.objects.delete() #todo narrow by measurement

    M.Measurement.objects(inspection = bson.ObjectId(params["id"])).delete()
    M.Result.objects(inspection = bson.ObjectId(params["id"])).delete()
    util.get_seer().reloadInspections()
    M.Inspection.inspect()
    #util.get_seer().update()


    return util.get_seer().inspections
  #except:
  #  return dict(status = "fail")

@route('/inspection_update', methods=['GET', 'POST'])
@util.jsonify
def inspection_update():
  try:
    params = request.values.to_dict()
    results = M.Inspection.objects(id = bson.ObjectId(params["id"]))
    if not len(results):
      return { "error": "no inspection id"}

    insp = results[0]

    if params.has_key("name"):
      insp.name = params["name"]

    if params.has_key("parameters"):
      insp.parameters = json.loads(params["parameters"])

    #TODO, add sorts, filters etc
    insp.save()
    return util.get_seer().inspections
  except:
    return dict(status = "fail")

@route('/measurement_add', methods=['GET', 'POST'])
@util.jsonify
def measurement_add():
  try:
    params = request.values.to_dict()
    if not params.has_key('units'):
      params['units'] = 'px';

    m = M.Measurement(name = params["name"],
      label = params['label'],
      method = params['method'],
      featurecriteria = json.loads(params["featurecriteria"]),
      parameters = json.loads(params["parameters"]),
      units = params['units'],
      inspection = bson.ObjectId(params['inspection']))
    m.save()

    #backfill?

    util.get_seer().reloadInspections()
    M.Inspection.inspect()
    #util.get_seer().update()

    return m
  except:
    return dict(status = "fail")

@route('/measurement_remove', methods=['GET', 'POST'])
@util.jsonify
def measurement_remove():
  try:
    params = request.values.to_dict()
    M.Measurement.objects(id = bson.ObjectId(params["id"])).delete()
    M.Result.objects(measurement = bson.ObjectId(params["id"])).delete()
    M.Watcher.objects.delete() #todo narrow by measurement

    util.get_seer().reloadInspections()
    #util.get_seer().update()

    return dict( remove = "ok")
  except:
    return dict(status = "fail")

@route('/measurement_results', methods=['GET', 'POST'])
@util.jsonify
def measurement_results(self, **params):
  try:
    params = request.values.to_dict()
    return list(M.Result.objects(measurement = bson.ObjectId(params["id"])).order_by("-capturetime"))
  except:
    return dict(status = "fail")

@route('/ping', methods=['GET', 'POST'])
@util.jsonify
def ping():
  text = "pong"
  return {"text": text }

@route('/olap/<olap_name>', methods=['GET'])
@util.jsonify
def olap(olap_name):
    o = M.OLAP.objects.get(name = olap_name)

    return o.execute()

@route('/olap/<olap_name>/since/<timestamp>', methods=['GET'])
@util.jsonify
def olap_since(olap_name, timestamp):
    o = M.OLAP.objects.get(name = olap_name)

    return o.execute(sincetime = int(timestamp))


@route('/plugin_js', methods=['GET', 'POST'])
def plugin_js():
  params = request.values.to_dict()

  js = ''
  for plugin in util.get_seer().plugins.keys():
    path = util.get_seer().pluginpath + "/" + plugin
    js += "//SimpleSeer plugin " + plugin + "\n\n"
    for f in [file for file in os.listdir(path) if re.search("js$", file)]:
      js += open(path + "/" + f).read()
  js += "\n\n\n";

  resp = make_response(js, 200)
  resp.headers['Content-Type'] = "application/javascript"
  return resp

@route('/start', methods=['GET', 'POST'])
def start():
  try:
    util.get_seer().start()
  except:
    util.get_seer().resume()
  return "OK"

@route('/stop', methods=['GET', 'POST'])
def stop():
  util.get_seer().stop()
  return "OK"

@route('/watcher_add', methods=['GET', 'POST'])
@util.jsonify
def watcher_add():
    params = request.values.to_dict()
    M.Watcher(**params).save()

    util.get_seer().reloadInspections()
    return util.get_seer().watchers

@route('/watcher_list_handlers', methods=['GET', 'POST'])
@util.jsonify
def watcher_list_handlers():
  return [s for s in dir(M.Watcher) if re.match("handler_", s)]

@route('/watch_remove', methods=['GET', 'POST'])
@util.jsonify
def watcher_remove():
  params = request.values.to_dict()
  M.Watcher.objects(id = bson.ObjectId(params["id"])).delete()

  util.get_seer().reloadInspections()
  return util.get_seer().watchers
