import json
import pprint
import requests

url = 'http://localhost:8080/frames'

def main():
    for filters, sorts in params:
        result =  requests.get(
            url, params=dict(
                filter=json.dumps(filters),
                sort=json.dumps(sorts),
                limit=5))
        if not result.ok:
            print result
            import pdb; pdb.set_trace()
        assert result.ok
        print '===='
        print 'filters:'
        pprint.pprint(filters)
        print 'sorts:'
        pprint.pprint(sorts)
        print 'response:'
        print len(result.json)
        for doc in result.json:
            for f in doc['features']:
                if f['featuretype'] != 'Blob': continue
                print f['featuredata']['mArea']
                break
        # pprint.pprint(result.json)

params=[
    # ({}, {}),
    ({'features.featuretype': 'Blob',
      'features.featuredata.mArea': {'$gt': 230000} },
     {'features.featuredata.mArea': -1 })
    ]
    
if __name__ == '__main__':
    main()
