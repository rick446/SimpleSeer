from .base import Command

class ScriptCommand(Command):
    "Run a user-defined script in the seer 'context'"
    # use_gevent = 'Configurable by command line'
    remote_seer = True

    def __init__(self, subparser):
        subparser.add_argument('-g', '--use-gevent', action='store_true')
        subparser.add_argument('script')

    def configure(self, options):
        self.use_gevent = options.use_gevent
        super(ScriptCommand, self).configure(options)

    def run(self):
        from SimpleSeer import models as M
        from SimpleSeer.realtime import ChannelManager
        from .. import util
        util.load_plugins()
        ns = dict(
            M=M, CM=ChannelManager(), self=self)
        with open(self.options.script) as fp:
            exec fp in ns,ns
