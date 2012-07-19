import os as os

class InspectionPlugin(object):

    def __init__(self, inspection):
        self.inspection = inspection

    @classmethod
    def printFields(cls):
        return ["x", "y", "width", "height","area"]
	
    @classmethod
    def coffeescript(cls):
        ext = ".coffee"
        #Get the subclass name and location
        stem = cls.__name__.split('.')[-1]
        path = __import__(cls.__module__).__file__
        # slice it up, and set it to the coffeescript path
        s = path.split('/')
        path = path[0:len(path)-len(s[-1])] #pull of the filename
        path = path + "plugins/"+stem+"/cs/"+stem #add the plugin name
        
        # yield the inspection coffeescript file 
        mpath = path+"Inspection"+ext
        if( os.path.exists(mpath) ):
            f = open( mpath, 'r' )
            yval = f.read()
            # print("Inspection+++++++++++++++++++++++")
            # print(mpath)
            # print(yval)
            # print("+++++++++++++++++++++++++++++++++")

            yield 'models/inspection', yval 
        else:
            yield 'models/inspection', '' 
        #yield the feature coffeescript file 
        mpath = path+"Feature"+ext
        if( os.path.exists(mpath) ):
            f = open( mpath, 'r' )
            yval = f.read()
            # print("Feature++++++++++++++++++++++++++")
            # print(mpath)
            # print(yval)
            # print("+++++++++++++++++++++++++++++++++")
            yield 'models/feature', yval 
        else:
            yield 'models/feature', '' 



    def __call__(self, image):
        raise NotImplementedError, '__call__'

class MeasurementPlugin(object):

    def __init__(self, measurement):
        self.measurement = measurement

    @classmethod
    def coffeescript(cls): return ''

    def __call__(self, frame, featureset):
        raise NotImplementedError, '__call__'

class WatcherPlugin(object):

    def __init__(self, watcher):
        self.watcher = watcher

    @classmethod
    def coffeescript(cls): return ''

    def __call__(self, messages):
        raise NotImplementedError, '__call__'
