class InspectionPlugin(object):

    def __init__(self, inspection):
        self.inspection = inspection

    def __call__(self, image):
        raise NotImplementedError, '__call__'

class MeasurementPlugin(object):

    def __init__(self, measurement):
        self.measurement = measurement

    def __call__(self, frame, featureset):
        raise NotImplementedError, '__call__'

class WatcherPlugin(object):

    def __init__(self, watcher):
        self.watcher = watcher

    def __call__(self, messages):
        raise NotImplementedError, '__call__'
