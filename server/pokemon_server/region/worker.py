# coding:utf-8
import os


class Worker(object):

    def __init__(self, id):
        self.id = id

    @property
    def pid(self):
        return os.getpid()

    def run(self):
        raise NotImplementedError()

    def init_process(self):
        self.run()
