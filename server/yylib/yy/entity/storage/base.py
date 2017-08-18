# coding: utf-8
import traceback
from yy.entity.base import EntityNotFoundError

class EntityStoreMixinBase(object):
    next_id = 1
    identity_generator = None

    @classmethod
    def set_identity_generator(cls, gen):
        cls.identity_generator = gen

    def do_save(self):
        raise NotImplementedError

    def save(self, delay=True):
        import settings
        if delay and settings.DELAY_SAVE:
            return
        self.do_save()

    @classmethod
    def do_load(cls, entityID, fields=None):
        raise NotImplementedError

    @classmethod
    def get(cls, entityID):
        found = cls.do_load(entityID)
        if found:
            found.load_containers()
            found.pop_dirty()
            found.cycle()
            for cb in cls._listeners_on_load:
                cb(found)
            return found

    @classmethod
    def load(cls, entityID):
        result = cls.get(entityID)
        if result is None:
            raise EntityNotFoundError('Not found id `{}`'.format(entityID))
        return result

    @classmethod
    def simple_load(cls, entityID, fields):
        found = cls.do_load(entityID, fields)
        if found:
            found.pop_dirty()
            return found

    def delete(self):
        raise NotImplementedError

    @classmethod
    def do_create(cls, entityID=None):
        raise NotImplementedError

    @classmethod
    def create(cls, entityID=None, **kwargs):
        created = cls.do_create(entityID, **kwargs)
        for cb in cls._listeners_on_create:
            cb(created)
        return created

    @classmethod
    def get_attribute(cls, entityID, field):
        raise NotImplementedError

    @classmethod
    def get_attributes(cls, entityID, *names):
        raise NotImplementedError

    @classmethod
    def save_attributes(cls, entityID, **kwargs):
        raise NotImplementedError

    @classmethod
    def incr_attribute(cls, entityID, name, inc):
        raise NotImplementedError

    @classmethod
    def batch_load(cls, entityIDs, fields=None):
        raise NotImplementedError
