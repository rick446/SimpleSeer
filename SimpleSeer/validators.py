from datetime import datetime

import bson
from formencode import validators as fev

class ObjectId(fev.FancyValidator):

    def _to_python(self, value, state):
        if value is None: return None
        try:
            return bson.ObjectId(value)
        except bson.InvalidId:
            raise fev.Invalid('invalid object id', value, state)

    def _from_python(self, value, state):
        if value is None: return None
        return str(value)

class JSON(fev.FancyValidator):

    def _to_python(self, value, state):
        if value is None: return None
        if isinstance(value, dict):
            return value
        raise fev.Invalid('invalid JSON document', value, state)

    def _from_python(self, value, state):
        if value is None: return None
        if isinstance(value, dict):
            return value
        raise fev.Invalid('invalid Python dict', value, state)

class DateTime(fev.FancyValidator):

    def _to_python(self, value, state):
        try:
            return datetime.strptime(value, '%Y-%m-%dT%H:%M:%S.%fZ')
        except ValueError, ve:
            raise fev.Invalid(str(ve), value, state)

    def _from_python(self, value, state):
        return value.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
