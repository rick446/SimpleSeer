import time
import logging
from datetime import datetime

import pkg_resources
import mongoengine

from SimpleCV import Image

log = logging.getLogger(__name__)

class SimpleDoc(object):
    _jsonignore = [None]
    
    
    def __getstate__(self):  
        ret = {}
        ret['id'] = self.id

        for k in self._data.keys():
            if k == 'id': continue
            if not k:
                continue
              
            v = self._data[k]
            if k[0] == "_" or k in self._jsonignore:
                continue
            if (hasattr(v, "__json__")):
                ret[k] = v.__json__()
            elif isinstance(v, datetime):
                ret[k] = int(time.mktime(v.timetuple()) + v.microsecond/1e6)
            elif isinstance(v, mongoengine.fields.GridFSProxy):
                if v is None:
                    ret[k] = None
                else:
                    ret[k] = "/grid/"+k+"/" + str(self.id)
            else:
                ret[k] = v
            
        return ret

    def update_from_json(self, d):
        for k,v in d.items():
            setattr(self, k, v)
        
class SimpleEmbeddedDoc(object):
    """
    Any embedded docs (for object trees) should extend SimpleEmbeddedDoc
    """
    _jsonignore = [None]
    
class WithPlugins(object):

    def get_plugin(self, name):
        '''Get a named plugin and instantiate it with the model instance'''
        try:
            PluginClass = self._plugins[name]
        except AttributeError:
            cls = self.__class__
            raise ValueError, ('No plugins registered on %r, maybe you need to'
                               'call %s.register_plugins(group)?' %
                               (cls, cls.__name__))
        except KeyError:
            raise ValueError, ('Plugin not found: %s. Valid plugins: %r' %
                               (name, self._plugins.keys()))
        return PluginClass(self)

    @classmethod
    def register_plugins(cls, group):
        if not hasattr(cls, '_plugins'):
            cls._plugins = {}
        for ep in pkg_resources.iter_entry_points(group):
            log.info('Loading %s plugin %s', group, ep.name)
            try:
                cls._plugins[ep.name] = ep.load()
            except Exception, err:
                log.error('Failed to load %s plugin %s: %s', group, ep.name, err)
