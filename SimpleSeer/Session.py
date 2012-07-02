import json
import logging
from gevent import monkey
import mongoengine

class Session():
    """
    The session singleton must be instantiated with a configuration file reference
    as it's sole parameter before any of the SimpleSeer classes are imported.  This
    is due to all of Ming's relational computations happening at import-time,
    so a database connection must be provided.
    
    Once initialized, Session() can be used to reference configuration options
    globaly.  To refresh configuration options, simply call again with a different
    or updated config file.

    Session will default to "" any properties which are non-existant.  This is 
    nice, because it eliminates a lot of "try" blocks as you update the code
    (and potentially not the config file).  But it also can shoot you in the
    foot if you misspell property names.  Be careful!    
    """
    __shared_state = dict(
        _config = {})
    
    def __init__(self, json_config = ''):
        self.__dict__ = self.__shared_state
        
        if not json_config:
            return  #return the existing shared context

        config_dict = json.load(open(json_config), object_hook=_decode_dict)
        self.configure(config_dict)

    def configure(self, d):
        from .models.base import SONScrub
        self._config = d
        self.mongo['use_greenlets'] = True  #use greenlet-safe connection pooling 
        mongoengine.connect(self.database, **self.mongo)
        db = mongoengine.connection.get_db()
        db.add_son_manipulator(SONScrub())
        self.log = logging.getLogger(__name__)

    def get_config(self):
        return self._config

    def __getattr__(self, name):
        return self._config.get(name, '')

    def __repr__(self):
        return "SimpleSeer Session Object"

#code to convert unicode to string
# http://stackoverflow.com/questions/956867/how-to-get-string-objects-instead-unicode-ones-from-json-in-python
def _decode_list(lst):
    newlist = []
    for i in lst:
        if isinstance(i, unicode):
            i = i.encode('utf-8')
        elif isinstance(i, list):
            i = _decode_list(i)
        newlist.append(i)
    return newlist

def _decode_dict(dct):
    newdict = {}
    for k, v in dct.iteritems():
        if isinstance(k, unicode):
            k = k.encode('utf-8')
        if isinstance(v, unicode):
             v = v.encode('utf-8')
        elif isinstance(v, list):
            v = _decode_list(v)
        newdict[k] = v
    return newdict   
    
