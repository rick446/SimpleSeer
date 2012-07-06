from OLAP import OLAP
from numpy.linalg import qr, solve
from numpy import dot

import mongoengine
from .base import SimpleDoc


class Inferential(SimpleDoc, mongoengine.Document):

    olaps = mongoengine.ListField()
    inds = mongoengine.ListField()
    dep = mongoengine.StringField()
    coeff = mongoengine.ListField()
    method = mongoengine.StringField()
    
    def __repr__(self):
        return "<Inferential %s: %s>" % (self.method, self.olap)
    
    
    def execute(self):
      
        o = OLAP.objects(name=self.olap)[0]
        o.limit = 1
        data = o.execute()[0]
        
        return sum([(data[key] * coeff) for key, coeff in zip(self.inds, self.coeff[1:])]) + self.coeff[0]
        
        
    def rerun(self):
        # Recomput the coefficients for this model
        if self.method == 'ols':
            self.coeff = self.olsCoeff()
            self.save()
    
    def getData(self):
        
        o = OLAP.objects(name=o.name)[0]
        rawData = o.execute()
        
        i = []
        d = []
        
        for r in rawData:
            row = [ r[k] for k in self.inds ]
            i.append(row)            
            d.append(r[self.dep])  

        return [d, i]

    def olsCoeff(self):
        [y, X] = self.getData()
        
        [Q, R] = qr(X)
        return solve(R, dot(Q.T, y)) 

        
