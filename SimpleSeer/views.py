import os
import re
import json
import logging
import calendar
from datetime import datetime
from cStringIO import StringIO

import bson.json_util
import gevent
import coffeescript
from socketio import socketio_manage
from flask import request, make_response, Response

from . import models as M
from . import util
from .realtime import RealtimeNamespace, ChannelManager
from .service import SeerProxy2
from .Session import Session

log = logging.getLogger()

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
    return open(os.path.join(os.path.dirname(__file__), 'static/public/index.html')).read()

@route('/plugins.js')
def plugins():
    seer = SeerProxy2()
    result = []
    for ptype, plugins in seer.plugins.items():
        for name, plugin in plugins.items():
            for requirement, cs in plugin.coffeescript():
                result.append('(function(plugin){')
                try:
                    result.append(coffeescript.compile(cs, True))
                except Exception, e:

                    print "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
                    print "COFFEE SCRIPT ERROR"
                    print e
                    print "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"

                result.append('}).call(require(%r), require("lib/plugin"));\n' % requirement)
    resp = make_response("\n".join(result), 200)
    resp.headers['Content-Type'] = "text/javascript"
    return resp

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
    seer = SeerProxy2()
    result = seer.get_image(**params)
    resp = make_response(result['data'], 200)
    resp.headers['Content-Type'] = result['content_type']
    return resp

@route('/lastframes', methods=['GET'])
@util.jsonify
def lastframes():
    params = request.values.to_dict()
    frames = M.Frame.objects().order_by("-capturetime")
    if 'before' in params:
        frames = frames.filter(capturetime__lte=datetime.fromtimestamp(int(params['before'])))
    total_frames = frames.count()
    frames = frames.skip((int(params.get('page', 1))-1)*20).limit(20)
    return dict(frames=list(frames), total_frames=total_frames)

@route('/frames', methods=['GET'])
@util.jsonify
def frames():
    params = request.values.to_dict()
    f_params = json.loads(
        params.get('filter', '[]'),
        object_hook=util.object_hook)
    s_params = json.loads(
        params.get('sort', '[]'),
        object_hook=util.object_hook)
    skip = int(params.get('skip', 0))
    limit = int(params.get('limit', 20))
    total_frames, frames, earliest_date = M.Frame.search(f_params, s_params, skip, limit)
    if earliest_date:
        earliest_date = calendar.timegm(earliest_date.timetuple())
    return dict(frames=frames, total_frames=total_frames, earliest_date=earliest_date)

#TODO, abstract this for layers and thumbnails        
@route('/grid/imgfile/<frame_id>', methods=['GET'])
def imgfile(frame_id):
    params = request.values.to_dict()
    frame = M.Frame.objects(id = bson.ObjectId(frame_id))
    if not frame or not frame[0].imgfile:
        return "Image not found", 404
    frame = frame[0]
    resp = make_response(frame.imgfile.read(), 200)
    resp.headers['Content-Type'] = frame.imgfile.content_type
    if 'download' in params:
        resp.headers['Content-disposition'] = 'attachment; filename="%s-%s.jpg"' % \
            (frame.camera.replace(' ','_'), frame.capturetime.strftime("%Y-%m-%d_%H_%M_%S"))

    return resp    

#TODO, abstract this for layers and thumbnails        
@route('/grid/thumbnail_file/<frame_id>', methods=['GET'])
def thumbnail(frame_id):
    params = request.values.to_dict()
    frame = M.Frame.objects(id = bson.ObjectId(frame_id))
    if not frame or not frame[0].imgfile:
        return "Image not found", 404
    frame = frame[0]
    
    if not frame.thumbnail_file:
        t = frame.thumbnail
        if not "is_slave" in Session().mongo or not Session().mongo['is_slave']:
            frame.save()
        else:
            s = StringIO()
            t.save(s, "jpeg", quality = 75)
            resp = make_response(s.getvalue(), 200)
            resp.headers['Content-Type'] = "image/jpeg"
            return resp
   
    resp = make_response(frame.thumbnail_file.read(), 200)
    resp.headers['Content-Type'] = frame.thumbnail_file.content_type
    return resp    


@route('/videofeed-width<int:width>-camera<int:camera>.mjpeg', methods=['GET'])
def videofeed(width=0, camera=0):    
    params = {
        'width': width,
        'index': -1,
        'camera': camera,
        }
    params.update(request.values)
    

    seer = SeerProxy2()
    log.info('Feeding video in greenlet %s', gevent.getcurrent())
    def generate():        
        socket = ChannelManager().subscribe("capture/")
        
        while True:
            img = seer.get_image(**params)
            yield '--BOUNDARYSTRING\r\n'
            yield 'Content-Type: %s\r\n' % img['content_type']
            yield 'Content-Length: %d\r\n' % len(img['data'])

            yield '\r\n'
            yield img['data']
            yield '\r\n'
            gevent.sleep(0)
            socket.recv() #we actually ignore the message
    return Response(
        generate(),
        headers=[
            ('Connection', 'close'),
            ('Max-Age', '0'),
            ('Expires', '0'),
            ('Cache-Control', 'no-cache, private'),
            ('Pragma', 'no-cache'),
            ('Content-Type',
             "multipart/x-mixed-replace; boundary=--BOUNDARYSTRING") ])


@route('/videofeed-width<int:width>.mjpeg', methods=['GET'])
def videofeed_width_only(width=0):
	return videofeed(width)

@route('/videofeed-camera<int:camera>.mjpeg', methods=['GET'])
def videofeed_camera_only(camera=0):
    return videofeed(0,camera)

@route('/videofeed.mjpeg', methods=['GET'])
def videofeed_camera_res():
    return videofeed()
    

@route('/frame_capture', methods=['GET', 'POST'])
@util.jsonify
def frame_capture():
    seer = util.get_seer()
    seer.capture()
    seer.inspect()
    seer.update()
    return dict( capture = "ok" )

@route('/frame_inspect', methods=['GET', 'POST'])
@util.jsonify
def frame_inspect():
    seer = util.get_seer()
    try:
        seer.inspect()
        seer.update()
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
        seer = util.get_seer()
        M.Inspection(
            name = params.get("name"),	
            camera = params.get("camera"),
            method = params.get("method"),
            parameters = json.loads(params.get("parameters"))).save()
        seer.reloadInspections()
        seer.inspect()
        #util.get_seer().update()
        return seer.inspections()
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
    seer = util.get_seer()
    M.Inspection.objects(id = bson.ObjectId(params["id"])).delete()
    #for m in Measurement.objects(inspection = bson.ObjectId(params["id"])):
    M.Watcher.objects.delete() #todo narrow by measurement

    M.Measurement.objects(inspection = bson.ObjectId(params["id"])).delete()
    M.Result.objects(inspection_id = bson.ObjectId(params["id"])).delete()
    seer.reloadInspections()
    seer.inspect()
    #util.get_seer().update()


    return seer.inspections
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
        seer = util.get_seer()
        seer.reloadInspections()
        seer.inspect()
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
        M.Result.objects(measurement_id = bson.ObjectId(params["id"])).delete()
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
    
#todo: move settings to mongo, create model with save
@route('/settings', methods=['GET', 'POST'])
@util.jsonify
def settings():
    text = Session().get_config()
    return {"settings": text }

@route('/chart/<chart_name>', methods=['GET'])
@util.jsonify
def chart(chart_name):
    c = M.Chart.objects.get(name = chart_name)
    
    return c.createChart()

@route('/chart/<chart_name>/since/<timestamp>', methods=['GET'])
@util.jsonify
def chart_since(chart_name, timestamp):
    c = M.Chart.objects.get(name = chart_name)

    return c.createChart(sincetime = int(float(timestamp)))

@route('/chart/<chart_name>/since/<sincetimestamp>/before/<beforetimestamp>', methods=['GET'])
@util.jsonify
def chart_since_before(chart_name, sincetimestamp, beforetimestamp):
    c = M.Chart.objects.get(name = chart_name)

    return c.createChart(sincetime = int(float(sincetimestamp)), beforetime = int(float(beforetimestamp)))



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

@route('/_status', methods=['GET', 'POST'])
def status():
    return 'ok'
