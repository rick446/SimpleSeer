from SimpleSeer import models as M
from SimpleSeer.plugins import base
from SimpleCV import Color
from sklearn import tree
import marshal, types



class ClosestColorMLMeasurement(base.MeasurementPlugin):
    def __init__(self,path="./"):
        
        pklfile = "ClosestColorML.pkl"
        pklfile = path + pklfile
        if( not os.path.exists(pklfile) ):
            warnings.warn("Could not find ML data. Everything is borked.")
            return
        self.mlDict = pickle.load(open(pklfile,"r"))
        code = marshal.loads(mlDict["feature_extractor"])
        self.feature_extractor = types.FunctionType(code, globals(), "feature_extractor")
        self.mask = Image(path+mlDict["maskFile"])
        self.dtree = mlDict["dtree"]
        self.labels= mlDict["label_strings"]
        self.pallette = mlDict["color_map"] 

    def __call__(self, frame, features):        
        w = frame.image.width
        h = frame.image.height
        result = None
        if( w != self.mask.width or h != self.mask.height ):
            mask = self.mask.reize(w,h)
            fv = self.feature_extractor(frame.image,mask)
            guess = self.dtree.predict(fv)
            result = self.color_map[guess[0]]
        else:
            fv = self.feature_extractor(frame.image,self.mask)
            guess = self.dtree.predict(fv)
            result = self.color_map[guess[0]]
                    
        return [result]
