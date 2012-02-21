from SimpleSeer.plugins.base import *
from twilio.rest import TwilioRestClient



def sendsms(number, text):
    SS = SimpleSeer.SimpleSeer()
    client = TwilioRestClient(SS.config.twilio_account_sid, SS.config.twilio_auth_token)
    message = client.sms.messages.create(
        to="+" + str(int(number)),
        from_= SS.config.twilio_from_number,
        body= text)

def handler_smsalert(self, messages):
    for m in messages:
        if not m.passed:
            sendsms(m.number, "Houston, we have a problem")
            
Watcher.handler_smsalert = handler_smsalert

import SimpleSeer.SimpleSeer
