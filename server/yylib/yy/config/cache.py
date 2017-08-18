# coding: utf-8
import ujson
from .configs import *
from .dump import dump

_config_cache = {}


def get_config(cls):
    return _config_cache[cls.__name__]


def get_config_by_name(clsname):
    return _config_cache[clsname]


def load(configs, path, **sources):
    result = ujson.loads(dump(configs, path, **sources))
    cache = {}
    for cls in configs:
        container = cache[
            cls.__name__] = cls.__Meta__.dict_class() if cls.haskey() else []
        for row in result[cls.__name__]:
            obj = cls.namedtuple(*row)
            if not cls.haskey():
                container.append(obj)
            else:
                key, grouped = cls.getkey(obj._asdict())
                if grouped:
                    if cls.subkey_field is None:
                        if key not in container:
                            container[key] = []
                        container[key].append(obj)
                    else:
                        if key not in container:
                            container[key] = {}
                        container[key][
                            getattr(
                                obj,
                                cls.subkey_field.name)] = obj
                else:
                    container[key] = obj
    _config_cache.update(cache)
