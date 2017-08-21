# coding:utf-8
import raven
import settings
import gevent
from gevent.queue import Queue
from raven.transport import HTTPTransport


class SentryClient(object):

    def __init__(self):
        if settings.SERVER_DSN:
            self.__client = raven.Client(dsn=settings.SERVER_DSN, transport=HTTPTransport)
            self.queue = Queue()
            self.loop = None

    def send(self, exc_info, **kwargs):
        if settings.SERVER_DSN:
            data = self.__client.build_msg('raven.events.Exception', exc_info=exc_info, **kwargs)
            self.queue.put(data)
            if not self.loop:
                self.__start()

    def __run(self):
        while True:
            data = self.queue.get()
            self.__client.send(**data)

    def __start(self):
        self.loop = gevent.spawn(self.__run)
        self.loop.start()

    def __stop(self):
        self.loop.stop()
        self.loop = None
