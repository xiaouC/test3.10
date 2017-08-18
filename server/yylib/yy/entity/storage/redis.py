# coding:utf-8
from yy.entity.base import EntityExistsException,  EntityNotFoundError
from yy.utils import group_list_by_two
from .base import EntityStoreMixinBase

def make_key(tag, entityID):
    return '%s{%d}'%(tag, entityID)

class EntityStoreMixinRedis(EntityStoreMixinBase):
    pool = None

    def make_key(self):
        assert self.entityID > 0
        return make_key(type(self).store_tag, self.entityID)

    def do_save(self):
        dirty_values = self.pop_dirty_values()
        cmd = ['HMSET', self.make_key()]
        for key, value in dirty_values:
            cmd.append(key)
            cmd.append(value)
        extra_cmds = self.dirty_commands
        self.dirty_commands = []
        if not dirty_values and not extra_cmds:
            return
        self.pool.execute_pipeline(cmd, *extra_cmds)

    @classmethod
    def do_load(cls, entityID, fields=None):
        key = make_key(cls.store_tag, entityID)
        # check exists

        if fields is None:
            result = list(group_list_by_two(cls.pool.execute('HGETALL', key)))
            if not result:
                return
        else:
            fields = ['entityID'] + list(fields)
            result = cls.pool.execute('HMGET', key, *fields)
            if not result[0]:
                return
            result = zip(fields, result)

        obj = cls(entityID=entityID)
        obj.begin_initialize()
        for name, item in result:
            if item is None:
                continue
            try:
                f = cls.fields[name]
            except KeyError:
                continue
            if f.decoder is not None:
                item = f.decoder(item)
            setattr(obj, name, item)
        obj.end_initialize()

        return obj

    @classmethod
    def do_create(cls, entityID=None, **kwargs):
        entityID = entityID or cls.identity_generator.gen()
        key = make_key(cls.store_tag, entityID)
        if cls.pool.execute('EXISTS', key):
            raise EntityExistsException(key)
        obj = cls(entityID=entityID)
        for k, v in kwargs.items():
            setattr(obj, k, v)
        return obj

    def delete(self):
        self.pool.execute('DEL', self.make_key())

    @classmethod
    def get_attribute(cls, entityID, name):
        return cls.pool.execute('HGET', make_key(cls.store_tag, entityID), name)

    @classmethod
    def get_attributes(cls, entityID, *names):
        return cls.pool.execute('HMGET', make_key(cls.store_tag, entityID), *names)

    @classmethod
    def save_attributes(cls, entityID, **kwargs):
        key = make_key(cls.store_tag, entityID)
        cmd = ['HMSET', key]
        for name, value in kwargs.items():
            cmd.append(name)
            cmd.append(value)
        return cls.pool.execute(*cmd)

    @classmethod
    def incr_attribute(cls, entityID, name, inc):
        key = make_key(cls.store_tag, entityID)
        return cls.pool.execute('HINCRBY', key, name, inc)

    @classmethod
    def batch_load(cls, entityIDs, names=None):
        if names is None:
            cmds = [['HGETALL', make_key(cls.store_tag, entityID)] for entityID in entityIDs]
        else:
            names = ['entityID'] + list(names)
            cmds = [['HMGET', make_key(cls.store_tag, entityID)] + names for entityID in entityIDs]
        result = []
        for rsp in cls.pool.execute_pipeline(*cmds):
            if names is None:
                temp = dict(group_list_by_two(rsp))
                if not temp or not temp.get('entityID'):
                    # not found
                    result.append(None)
                    continue
            else:
                if not rsp[0]:
                    # not found
                    result.append(None)
                    continue
                temp = dict(zip(names, rsp))

            obj = cls(entityID=int(temp['entityID']))
            obj.begin_initialize()
            for name, item in temp.items():
                if item is None:
                    continue
                try:
                    f = cls.fields[name]
                except KeyError:
                    continue
                if f.decoder is not None:
                    item = f.decoder(item)
                setattr(obj, name, item)
            obj.end_initialize()

            if names is None:
                # 全量
                obj.load_containers()
                obj.cycle()
                for cb in cls._listeners_on_load:
                    cb(obj)

            obj.pop_dirty()
            result.append(obj)
        return result
