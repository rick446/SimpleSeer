from SimpleSeer.plugins.base import *

def sendsms(number, message):
    print 'sent "%s" to %s', (number, message)

def handler_smsalert(self, messages):
    for m in messages:
        if not m.passed:
            sendsms(m.number, m.label)
            
Watcher.handler_smsalert = handler_smsalert