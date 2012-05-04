import sys
import logging
import threading
from functools import partial

import zmq
from IPython.zmq.ipkernel import IPKernelApp
from SimpleCV.Shell import setup_shell

from .realtime import ChannelManager

log = logging.getLogger(__name__)

INPROC = False

class patch(object):

    def __init__(self, obj):
        self._obj = obj

    def __call__(self, func):
        name = func.func_name
        old_func = getattr(self._obj, name)
        setattr(self._obj, name, partial(func, old_func))
        return func

class SeerKernel(object):

    def __init__(self, seer):
        self.seer = seer

    def run(self):
        logging.getLogger('IPKernelApp').disabled = True
        app = IPKernelApp.instance()
        app.connection_file='kernel-simpleseer.json'
        app.initialize()
        app.shell.user_ns.update(
            seer=self.seer,
            cm=ChannelManager(zmq.Context.instance()))
        log.info('Kernel is running on %s', app.connection_file)
        self.seer.config.connection_file = app.connection_file
        app.start()

def anotebook():
    from IPython.frontend.html.notebook.notebookapp import NotebookApp
    app = NotebookApp()
    app.open_browser=False
    app.port = 8889
    app.initialize()
    t = threading.Thread(target=app.start)
    t.daemon = True
    t.start()

def shell(listener):
    '''Runs a simple embedded SimpleCV shell that communicates over sockets'''
    from IPython.utils import io
    from SimpleCV.Shell import setup_shell

    def handle(socket, address):
        scvShell = setup_shell()
        stderr = io.IOStream(socket.makefile('w', 0))
        stdout = io.IOStream(socket.makefile('w', 0))

        @patch(scvShell)
        def raw_input_original(func, prompt=''):
            if prompt:
                socket.send(prompt)
                result = socket.recv(1024)
                if not result:
                    scvShell.exiter()
                return result

        @patch(scvShell)
        def write(func, data):
            socket.send(data)

        @patch(scvShell)
        def init_io(func):
            io.stdout = stdout
            io.stderr = stderr

        @patch(scvShell)
        def _showtraceback(func, etype, evalue, stb):
            if io.stdout.stream != stdout:
                scvShell.init_io()
            return func(etype, evalue, stb)

        scvShell.init_io()
        scvShell()
        print >> stderr, '\nGood-bye\n\n'
        socket.shutdown(gevent.socket.SHUT_RDWR)
        socket.close()

    return StreamServer(listener, handle)


def run_shell(parent, shell):
    shell()
    parent.stop()

class ShellThread(threading.Thread):

    def __init__(self):
        super(ShellThread, self).__init__()
        self._stop = threading.Event()

    def stop(self):
        self._stop.set()

    def stopped(self):
        return self._stop.isSet()

    def run(self):
        scvShell = setup_shell()
        sys.exit(run_shell(self, scvShell))

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    shell(('0.0.0.0', 8080)).serve_forever()
