from pprint import pprint
import bson
import formencode as fe
from flask import request
from flask import Blueprint
from flask_rest import RESTResource, SERIALIZERS
from formencode import validators as fev
from formencode import schema as fes

from .base import jsonencode
from . import validators as V

# SERIALIZERS expects and 'encode' property in its encoders
jsonencode.encode = jsonencode
SERIALIZERS['application/json'] = jsonencode

def register(app):
    import Inspection

    bp = Blueprint("api", __name__, url_prefix="/api")

    handlers = [
        ModelHandler(Inspection.Inspection, InspectionSchema,
                     'inspection', '/inspections') ]

    for h in handlers:
        RESTResource(app=bp, name=h.name, route=h.route,
                     actions=["list", "add", "update", "delete", "get"],
                     handler=h)

    # RESTResource(
    #     app=bp, # the app which should handle this
    #     name="inspection", # name of the var to inject to the methods
    #     route="/inspections",  # will be availble at /api/inspections/*
    #     actions=["list", "add", "update", "delete", "get"], #authorised actions
    #     handler=ModelHandler(Inspection)) # the handler of the request

    app.register_blueprint(bp)

class InspectionSchema(fes.Schema):
    _id = V.ObjectId(if_empty=bson.ObjectId, if_missing=None)
    parent = V.ObjectId(if_empty=None, if_missing=None)
    name = fev.UnicodeString(not_empty=True)
    method = fev.UnicodeString(not_empty=True)
    camera = fev.UnicodeString(not_empty=True)
    parameters = V.JSON(if_empty=dict, if_missing=None)
    filters = V.JSON(if_empty=dict, if_missing=None)
    richattributes = V.JSON(if_empty=dict, if_missing=None)
    morphs = fe.ForEach(fev.UnicodeString(), convert_to_list=True)

class ModelHandler(object):

    def __init__(self, cls, schema, name, route):
        self._cls = cls
        self.schema = schema()
        self.name = name
        self.route = route

    def add(self):
        try:
            values = self.schema.to_python(request.json, None)
        except fe.Invalid, inv:
            return 400, inv.unpack_errors()
        pprint(values)
        obj = self._cls(**values)
        obj.save()
        return 201, obj

    def update(self, inspection_id):
        try:
            id = bson.ObjectId(inspection_id)
            values = self.schema.to_python(request.json, None)
        except fe.Invalid, inv:
            return 400, inv.unpack_errors()
        objs = self._cls.objects(id=id)
        if not objs:
            return 404, {'error': 'Object not found'}
        obj = objs[0]
        obj.update_from_json(values)
        obj.save()
        return 200, obj

    def delete(self, inspection_id):
        try:
            id = bson.ObjectId(inspection_id)
        except fe.Invalid, inv:
            return 400, inv.unpack_errors()
        objs = self._cls.objects(id=id)
        if not objs:
            return 404, {'error': 'Object not found'}
        obj = objs[0]
        d = obj.__getstate__()
        obj.delete()
        return 200, d

    def get(self, inspection_id):
        try:
            id = bson.ObjectId(inspection_id)
        except fe.Invalid, inv:
            return 400, inv.unpack_errors()
        objs = self._cls.objects(id=id)
        if not objs:
            return 404, {'error': 'Object not found'}
        obj = objs[0]
        return 200, obj

    def list(self):
        objs = self._cls.objects()
        return 200, list(objs)
