import time
import gevent
from .base import Command

class CoreStatesCommand(Command):
    'Run the core server / state machine'
    use_gevent = True
    remote_seer = False

    def __init__(self, subparser):
        subparser.add_argument('program')
        subparser.add_argument('--disable-pyro', action='store_true')

    def run(self):
        from SimpleSeer.OLAPUtils import ScheduledOLAP
        from SimpleSeer.states import Core
        import Pyro4

        core = Core(self.session)
        with open(self.options.program) as fp:
            exec fp in dict(core=core)

        so = ScheduledOLAP()
        gevent.spawn_link_exception(so.runSked)

        core.start_socket_communication()

        if not self.options.disable_pyro:
            gevent.spawn_link_exception(core.run)
            Pyro4.Daemon.serveSimple(
                { core: "sightmachine.seer" },
                ns=True)
        else:
            core.run()

class CoreCommand(CoreStatesCommand):
    'Run the core server'

    def __init__(self, subparser):
        subparser.add_argument('--disable-pyro', action='store_true')

    def run(self):
        self.options.program = self.session.statemachine or 'default-states.py'
        super(CoreCommand, self).run()

@Command.simple(use_gevent=False, remote_seer=True)
def ControlsCommand(self):
    'Run a control event server'
    from SimpleSeer.Controls import Controls
    
    if self.session.arduino:
       Controls(self.session).run()

@Command.simple(use_gevent=False, remote_seer=False)
def PerfTestCommand(self):
    'Run the core performance test'
    from SimpleSeer.SimpleSeer import SimpleSeer
    from SimpleSeer import models as M

    self.session.auto_start = False
    self.session.poll_interval = 0
    seer = SimpleSeer()
    seer.run()

@Command.simple(use_gevent=True, remote_seer=True)
def WebCommand(self):
    'Run the web server'
    from SimpleSeer.Web import WebServer, make_app
    from SimpleSeer import models as M
    web = WebServer(make_app())
    web.run_gevent_server()

@Command.simple(use_gevent=True, remote_seer=True)
def BrokerCommand(self):
    'Run the message broker'
    from SimpleSeer.broker import PubSubBroker
    from SimpleSeer import models as M
    psb = PubSubBroker(self.session.pub_uri, self.session.sub_uri)
    psb.start()
    psb.join()

@Command.simple(use_gevent=False, remote_seer=True)
def ScrubCommand(self):
    'Run the frame scrubber'
    from SimpleSeer import models as M
    retention = self.session.retention
    if not retention:
        self.log.info('No retention policy set, skipping cleanup')
        return
    while retention['interval']:
        q_csr = M.Frame.objects(imgfile__ne = None)
        q_csr = q_csr.order_by('-capturetime')
        q_csr = q_csr.skip(retention['maxframes'])
        for f in q_csr:
            f.imgfile.delete()
            f.imgfile = None
            f.save(False)
        self.log.info('Purged %d frame files', q_csr.count())
        time.sleep(retention["interval"])

@Command.simple(use_gevent=False, remote_seer=True)
def ShellCommand(self):
    'Run the ipython shell'
    from IPython.config.loader import Config
    from IPython.frontend.terminal.embed import InteractiveShellEmbed
    from SimpleSeer.service import SeerProxy2
    from SimpleSeer import models as M

    banner = '''\nRunning the SimpleSeer interactive shell.\n'''
    exit_msg = '\n... [Exiting the SimpleSeer interactive shell] ...\n'
    shell= InteractiveShellEmbed(
        banner1=banner, exit_msg=exit_msg, user_ns={})
    shell.extension_manager.load_extension('SimpleSeer.ipython_extension')
    shell()

@Command.simple(use_gevent=False, remote_seer=True)
def NotebookCommand(self):
    'Run the ipython notebook server'
    from IPython.frontend.html.notebook import notebookapp
    from IPython.frontend.html.notebook import kernelmanager
    from SimpleSeer import models as M

    kernelmanager.MappingKernelManager.first_beat=30.0
    app = notebookapp.NotebookApp.instance()
    app.initialize([
            '--no-browser',
            '--port', '5050',
            '--ext', 'SimpleSeer.ipython_extension'])
    app.start()

