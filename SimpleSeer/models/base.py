import time
from datetime import datetime

from SimpleCV import Image

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
            elif isinstance(v, Image):
                ret[k] = v.applyLayers().getBitmap().tostring().encode("base64")
            elif isinstance(v, datetime):
                ret[k] = int(time.mktime(v.timetuple()) + v.microsecond/1e6)
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
    
