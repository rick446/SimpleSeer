from SimpleSeer import util
from SimpleSeer.plugins import base

from twilio.rest import TwilioRestClient

def sendsms(number, text):
    SS = util.get_seer()
    client = TwilioRestClient(
        SS.config.twilio_account_sid, SS.config.twilio_auth_token)
    client.sms.messages.create(
        to="+" + str(int(number)),
        from_= SS.config.twilio_from_number,
        body= text)

class SMSAlert(base.WatcherPlugin):

    def __call__(self, messages):
        for m in messages:
            if not m["passed"]:
                sendsms(m["number"], "Houston, we have a problem")
