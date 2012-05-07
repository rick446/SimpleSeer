import bson
import formencode as fe
import flask
import flask_rest
from formencode import validators as fev
from formencode import schema as fes
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
        ModelHandler(M.Inspection, InspectionSchema,
                     'inspection', '/inspections'),
		ModelHandler(M.OLAP, OLAPSchema,
					 'olap', '/olap')
       ]

    for h in handlers:
        flask_rest.RESTResource(
            app=bp, name=h.name, route=h.route,
            actions=["list", "add", "update", "delete", "get"],
            handler=h)

    app.register_blueprint(bp)


class InspectionSchema(fes.Schema):
    parent = V.ObjectId(if_empty=None, if_missing=None)
    name = fev.UnicodeString(not_empty=True)
    method = fev.UnicodeString(not_empty=True)
    camera = fev.UnicodeString(not_empty=True)
    parameters = V.JSON(if_empty=dict, if_missing=None)
    filters = V.JSON(if_empty=dict, if_missing=None)
    richattributes = V.JSON(if_empty=dict, if_missing=None)
    morphs = fe.ForEach(fev.UnicodeString(), convert_to_list=True)

class OLAPSchema(fes.Schema):
	name = fev.UnicodeString(not_empty=True)
	queryInfo = V.JSON(not_empty=True)
	descInfo = V.JSON(if_empty=None, if_missing=None)
	chartInfo = V.JSON(not_empty=True)
	
class QueryInfoSchema(fes.Schema):
	name = fev.UnicodeString(not_empty = True)
	since = V.DateTime(if_empty=0, if_missing=None)
	
class DescInfoSchema(fes.Schema):
	formula = fev.OneOf(['moving', 'mean', 'std'], if_missing=None)
	window = fev.Int(if_missing=None)

class ChartInfoSchema(fes.Schema):
	chartType = fev.OneOf(['line', 'bar', 'pie'])
	chartColor = fev.OneOf(['red', 'green', 'blue'])

class ModelHandler(object):

    def __init__(self, cls, schema, name, route):
        self._cls = cls
        self.schema = schema()
        self.name = name
        self.route = route

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
            values = self.schema.to_python(body, None)
        except fe.Invalid, inv:
            raise exceptions.BadRequest(inv.unpack_errors())
        return values

    def add(self):
        values = self._get_body(flask.request.json)
        obj = self._cls(**values)
        obj.save()
        return 201, obj

    def update(self, inspection_id):
        obj = self._get_object(inspection_id)
        values = self._get_body(flask.request.json)
        obj.update_from_json(values)
        obj.save()
        return 200, obj

    def delete(self, inspection_id):
        obj = self._get_object(inspection_id)
        d = obj.__getstate__()
        obj.delete()
        return 200, d

    def get(self, inspection_id):
        obj = self._get_object(inspection_id)
        return 200, obj

    def list(self):
        objs = self._cls.objects()
        return 200, list(objs)
