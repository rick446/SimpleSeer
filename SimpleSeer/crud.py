import bson
import formencode as fe
import flask
import flask_rest
from werkzeug import exceptions

from .base import jsonencode
from . import models as M
from . import validators as V

# SERIALIZERS expects and 'encode' property in its encoders
jsonencode.encode = jsonencode
flask_rest.SERIALIZERS['application/json'] = jsonencode

def register(app):
    bp = flask.Blueprint("api", __name__, url_prefix="/api")

    @bp.errorhandler(400)
    @bp.errorhandler(404)
    def errorhandler(error):
        result = getattr(error, 'description', {})
        if not isinstance(result, dict):
            result = dict(__error__=result)
        return flask.Response(
            jsonencode(result),
            status=error.code,
            mimetype='application/json')
            
        return error.description, error.code

    handlers = [
        ModelHandler(M.Inspection, M.InspectionSchema,
                     'inspection', '/inspection'),
        ModelHandler(M.OLAP, M.OLAPSchema, 'olap', '/olap'),
        ModelHandler(M.Measurement, M.MeasurementSchema, 'measurement', '/measurement'),
        ModelHandler(M.Frame, M.FrameSchema, 'frame', "/frame"),
        ModelHandler(M.FrameSet, M.FrameSetSchema, 'frameset', '/frameset'),
        ModelHandler(M.Chart, M.ChartSchema, 'chart', '/chart')
       ]

    for h in handlers:
        flask_rest.RESTResource(
            app=bp, name=h.name, route=h.route,
            actions= h.actions,
            handler=h)

    app.register_blueprint(bp)

class ModelHandler(object):

    def __init__(self, cls, schema, name, route,
                 actions = ("list", "add", "update", "delete", "get")):
        self._cls = cls
        self.schema = schema()
        self.name = name
        self.route = route
        self.actions = actions

    def _get_object(self, id):
        try:
            id = bson.ObjectId(id)
        except bson.errors.InvalidId:
            raise exceptions.NotFound('Invalid ObjectId')
        objs = self._cls.objects(id=id)
        if not objs:
            raise exceptions.NotFound('Object not found')
        return objs[0]

    def _get_body(self, body):
        try:
            try:
                del body['id']
            except KeyError:
                pass
            values = self.schema.to_python(body, None)
        except fe.Invalid, inv:
            raise exceptions.BadRequest(inv.unpack_errors())
        return values

    def add(self):
        values = self._get_body(flask.request.json)
        obj = self._cls(**values)
        obj.save()
        return 201, obj

    def update(self, **kwargs):
        id = kwargs.values()[0]
        obj = self._get_object(id)
        values = self._get_body(flask.request.json)
        obj.update_from_json(values)
        obj.save()
        return 200, obj

    def delete(self, **kwargs):
        id = kwargs.values()[0]


        obj = self._get_object(id)
        d = obj.__getstate__()
        obj.delete()
        return 200, d

    def get(self, **kwargs):
        id = kwargs.values()[0]

        obj = self._get_object(id)
        return 200, obj

    def list(self):
        objs = self._cls.objects()
        return 200, list(objs)
