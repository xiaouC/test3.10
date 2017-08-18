# coding:utf-8
from arbiter import Arbiter
from worker import Worker
from world.main import WorldServer


class WorldWorker(Worker):

    def __init__(self, id, **kwargs):
        super(WorldWorker, self).__init__(id)
        self.extra = kwargs

    def run(self):
        self.server = WorldServer(self.id, **self.extra)
        self.server.run()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-w', '--worlds', nargs='+', type=int, required=True)
    parser.add_argument('-i', '--ip', nargs="?", type=str)
    args = parser.parse_args()
    a = Arbiter(args.worlds, WorldWorker, ip=args.ip)
    a.run()
