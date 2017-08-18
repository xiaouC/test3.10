from gevent import Greenlet
from gevent.socket import socket
from gevent.queue import Queue

_close_message = object()

class AsyncSendSocket(socket):
    def __init__(self, *args, **kwargs):
        socket.__init__(self, *args, **kwargs)
        self._send_queue = Queue()
        self._send_thread = Greenlet.spawn(self._run_async_send)
        self._send_thread.link(self.on_thread_end)

    def on_thread_end(self, runner):
        self._send_thread = None

    def _run_async_send(self):
        _queue = self._send_queue
        while True:
            msg = _queue.get()
            if msg==_close_message:
                self.close()
                break
            else:
                #print 'async send', repr(msg)
                self.sendall(msg)

    def async_send(self, msg):
        #print 'async send', repr(msg)
        self._send_queue.put(msg)

    def async_close(self):
        if self._send_thread:
            self._send_queue.put(_close_message)
        else:
            self.close()

def async_send_socket(sock):
    '@sock: gevent.socket.socket'
    return AsyncSendSocket(_sock=sock)
