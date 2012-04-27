from base import *
from Session import Session


class Statistic(mongoengine.Document, base.SimpleDoc):
    """
    NOTE: this class is not tested code
    s = Statistic( {
       "name": "average of frame" + SimpleSeer().framecount,
       "capturetime": time.time() }) #we may want to put another ID field on here
       
    s.calculate(results, "average", np.mean)
    s.m.save()
    
    
    """
    data = mongoengine.DictField()
    name = mongoengine.StringField()
    capturetime = mongoengine.DateTimeField()
    results = mongoengine.ListField(mongoengine.ObjectField())

    def saveResults(self):
        for r in self.unsavedresults:
            r.save()
            self.results.append(r)

        del self.__dict__['unsavedresults']

    def calculate(self, results, name, column_function):
        measurement_group = {}
        
        self.unsavedresults = []
        
        for r in results:
            if not measurement_sort.has_key(r.measurement_id):
                measurement_sort[r.measurement_id] = []
                
            measurement_group[r.measurement_id].append(r.float_data)
            if r._id:
                self.results.append(r)
            else:
                self.unsavedresults.append(r)
                
        
        for m_id in measurement_group.keys():
            measurement = Measurement.m.get( _id = m_id )
            if not measurement.is_numeric:
                continue
            
            data_table = np.array(measurement_group[m_id])
            
            count = 0
            for label in measurement.result_labels:
                self.data[m._id][label] = column_function(data_table[:,count])
                count = count + 1
                
    def save(self):
        if len(self.unsavedresults):
            self.saveResults()
            self.m.save()


    #originally from the watcher function
    def threshold_greater(self, threshold, measurement_name, label, samples = 1):
        resultset = SimpleSeer().results[-samples:]
        measurement = Measurement.m.get( name = measurement_name )
        if not measurement:
            return False
            
        result_index = measurement.result_labels.index(label)
        if result_index == None:
            return False
        
        result_set = [ r for r in list if r.measurement_id == measurement._id ]
        
        stat = Statistic( {
            name: "Average of " + measurement_name,
            capturetime: time.time()
        })
        #MOVE THE ABOVE STUFF TO A DECORATOR
        
        stat.calculate(result_set, 'mean', np.mean)
        if stat.data[measurement._id][result_index] > threshold:
            return stat
        return False
    
    def log_statistics(self, statistics):
        for stat in statistics:
            stat.saveResults()
            stat.m.save()
