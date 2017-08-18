#coding:utf-8
from yy.utils import load_settings
load_settings()
#import config.loaders
from operator import add

from gevent import queue

class DBManager(object):
    def execute(self, *args, **kwargs):
        print 'execute', args, kwargs
    def async_execute(self, *args, **kwargs):
        print 'execute', args, kwargs

def patch_db():
    import db.manager
    db.manager.g_dbmanager = DBManager()

class WorldServer(object):
    def __init__(self, *args, **kwargs):
        from world import ctx
        ctx.worldServer = self

        from db.manager import start_dbmanager
        start_dbmanager()

    def notifyPlayerEnterResult(self, *args, **kwargs):
        print 'notifyPlayerEnterResult', args, kwargs

class socket(object):

    def __init__(self, *args, **kwargs):
        self.queue = queue.Queue()

    def send(self, *args, **kwargs):
        print 'socket send', args, kwargs

    def recv(self, *args, **kwargs):
        return self.queue.get()

    def async_send(self, *args, **kwargs):
        print 'async_send', args, kwargs
    def async_close(self, *args, **kwargs):
        print 'async_close', args, kwargs

class Entity(object):
    def __init__(self, id=None):
        self.entityID = id
        self.level = 1

    def save(self):
        pass

class PetBase(Entity):
    def __init__(self, id=None):
        super(PetBase, self).__init__(id)

    def sync_property(self, rsp):
        if not self.entityID:
            self.entityID = rsp.entityID
        for k, v in rsp.properties.__dict__.items():
            setattr(self, k, v)

class PlayerBase(Entity):
    def __init__(self, id=None):
        super(PlayerBase, self).__init__(id)
        self.pets = {}
        self.fbs = {}
        self.lineups = []
        self.vs = 0

    def update_fb(self, fbID, count):
        self.fbs[fbID] = count

    def get_fb_count(self, fbID):
        return self.fbs.get(fbID, 0)

    def get_fblinked(self):
        fbs = sorted(self.fbs.keys())
        return dict(zip(fbs, fbs[1:] + ([fbs[0]] if fbs else [])))

    def get_pet(self, petID):
        return self.pets.get(petID)

    def set_pet(self, pet):
        self.pets[pet.entityID] = pet

    def del_pet(self, petID):
        try:
            del self.pets[petID]
        except KeyError:
            pass

    def sync_property(self, rsp):
        if not self.entityID:
            self.entityID = rsp.entityID
        for k, v in rsp.properties.__dict__.items():
            setattr(self, k, v)

    def sync_pet_property(self, rsp):
        pet = self.get_pet(rsp.entityID)
        if not pet:
            pet = PetBase(rsp.entityID)
            self.set_pet(pet)
        pet.sync_property(rsp)

    def sync_scene_infos(self, rsp):
        for fb in rsp.fbs:
            self.fbs[fb.fbID] = fb.count

    def sync_lineups(self, rsp):
        for lineup in rsp.lineups:
            self.lineups.append(list(lineup.line))

    def get_pets(self):
        return self.pets.values()

    def get_lineup(self):
        lineup = self.lineups[1]
        result = []
        for pos, entityID in enumerate(lineup):
            if not entityID:
                continue
            pet = self.get_pet(entityID)
            result.append({
                'entityID':entityID,
                'prototypeID':pet.prototypeID,
                'level':pet.level,
                'pos':pos
            })
        return result

    def get_leader(self):
        return self.lineups[1][0]

    def get_valuable_pets(self):
        return [i.entityID for i in self.pets.values() if i.mtype == 0]

    def get_feeding_pets(self):
        return [i.entityID for i in self.pets.values() if i.mtype == 1]

    def get_evolution_pets(self):
        return [i.entityID for i in self.pets.values() if i.mtype == 2]

    def get_lineuped_pets(self):
        return filter(lambda s:s, set(reduce(add, self.lineups)))

    def get_futile_pets(self):
        return [i.entityID for i in self.pets.values()]

class Peer(object):
    def __init__(self, id):
        self._id = id
    def sender(self, msg):
        print 'send to', self._id, repr(msg)
