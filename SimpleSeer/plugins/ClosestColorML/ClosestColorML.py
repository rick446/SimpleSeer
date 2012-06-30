from SimpleSeer import models as M
from SimpleCV import *
from sklearn import tree
import marshal, types, os, pickle
from SimpleSeer.plugins import base

class ClosestColorMeasurementML(base.MeasurementPlugin):
    def __init__(self,stuff):
        print stuff
        path="./SimpleSeer/plugins/ClosestColorML/"
        fname = "ClosestColorML.pkl"
        pklfile = path + fname
        if( not os.path.exists(pklfile) ):
            warnings.warn("Could not find ML data. Everything is borked.")
            return
        mlDict = pickle.load(open(pklfile,"r"))
        code = marshal.loads(mlDict["feature_extractor"])
        self.feature_extractor = types.FunctionType(code, globals(), "feature_extractor")
        self.mask = Image(path+mlDict["maskFile"])
        self.dtree = mlDict["dtree"]
        self.labels= mlDict["label_strings"]
        self.color_map = mlDict["color_map"] 

    def __call__(self, frame, features):        
        w = frame.image.width
        h = frame.image.height
        result = None
        guess = [0]
        if( w != self.mask.width or h != self.mask.height ):
            mask = self.mask.reize(w,h)
            fv = self.feature_extractor(frame.image,mask)
            guess = self.dtree.predict(fv)
            result = self.labels[guess[0]]
        else:
            fv = self.feature_extractor(frame.image,self.mask)
            guess = self.dtree.predict(fv)
            result = self.labels[guess[0]]
        print "RESULT"+self.labels[guess[0]]
        if result == "fail" : # our fail color
            return [] 
        return [result]
