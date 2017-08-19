# coding:utf-8
import sys
import os
import importlib
from yy.utils import dictConfig


empty = object()


def new_method_proxy(func):
    def inner(self, *args):
        if self._wrapped is empty:
            self._setup()
        return func(self._wrapped, *args)
    return inner


class LazyObject(object):

    def __init__(self):
        self._wrapped = empty

    __getattr__ = new_method_proxy(getattr)

    def __setattr__(self, name, value):
        if name == "_wrapped":
            self.__dict__["_wrapped"] = value
        else:
            if self._wrapped is empty:
                self._setup()
            setattr(self._wrapped, name, value)

    def __delattr__(self, name):
        if name == "_wrapped":
            raise TypeError("Can't delete _wrapped.")
        if self._wrapped is empty:
            self._setup()
        delattr(self._wrapped, name)


def _resolve_name(name, package, level):
    """Return the absolute name of the module to be imported."""
    if not hasattr(package, 'rindex'):
        raise ValueError("'package' not set to a string")
    dot = len(package)
    for x in range(level, 1, -1):
        try:
            dot = package.rindex('.', 0, dot)
        except ValueError:
            raise ValueError("attempted relative import beyond top-level ",
                             "package")
    return "%s.%s" % (package[:dot], name)


def import_module(name, package=None):
    """Import a module.

    The 'package' argument is required when performing a relative import. It
    specifies the package to use as the anchor point from which to resolve the
    relative import to an absolute import.

    """
    if name.startswith('.'):
        if not package:
            raise TypeError("relative imports require the 'package' argument")
        level = 0
        for character in name:
            if character != '.':
                break
            level += 1
        name = _resolve_name(name[level:], package, level)
    __import__(name)
    return sys.modules[name]


class LazySettings(LazyObject):

    POEM_SETTINGS_VARIABLE = "POEM_SETTINGS"
    DEFAULT_SETTINGS = "local_settings"

    def get_settings_module(self):
        settings_module = os.environ.get(
            self.POEM_SETTINGS_VARIABLE, self.DEFAULT_SETTINGS)
        if not settings_module:
            settings_module = self.DEFAULT_SETTINGS
        return settings_module

    def _setup(self, **options):
        if self.configured:
            raise RuntimeError('Settings already configured.')
        settings_module = self.get_settings_module()
        self._wrapped = Settings(settings_module)
        self._wrapped.configure(**options)
        self._configure_logging()
        self._configure_redis()

    def _configure_logging(self):
        if self.LOG:
            dictConfig(self.LOG)

    def _configure_redis(self):
        if self.REDISES:
            # init redis
            from yy.db.redismanager import create_pool
            for k, v in self.REDISES.items():
                self.REDISES[k] = create_pool(v)

    def configure(self, **options):
        if not self.configured:
            self._setup(**options)
        self._wrapped.configure(**options)

    def watch(self, key=None, callback=None):
        if not self.configured:
            self._setup()
        if not callback:
            callback = lambda: self.configure()
        self._wrapped.watch(key=key, callback=callback)

    @property
    def configured(self):
        return self._wrapped is not empty


class Settings(object):

    def __init__(self, settings_module):
        self.GLOBAL_SETTINGS = "global_settings"
        self.SETTINGS_MODULE = self.GLOBAL_SETTINGS
        self.settings_module = settings_module
        self.options = {}
        self.configured = False
        # self.etcd = None

    def load_module(self, settings_module):
        try:
            mod = importlib.import_module(settings_module)
        except ImportError:
            raise ImportError(
                "Could not import settings '%s'. " % settings_module)
        else:
            return mod

    def _setup(self):
        sys.stderr.write("Using '%s'.\n" % self.SETTINGS_MODULE)
        # from __main__ import __package__
        # if __package__ == "scripts":
        #     return
        # import argparse
        # from conf.etcd_config import EtcdConfig
        # parser = argparse.ArgumentParser()
        # parser.add_argument('--etcd', type=str, default='')
        # parser.add_argument('-s', '--servers', nargs='+', type=int)
        # args = parser.parse_args()
        # if args.etcd:
        #     self.etcd = EtcdConfig(args.etcd, args.servers)
        # if self.etcd:
        #     self.options.update(self.etcd.info())

    def configure(self, **options):
        # 优先local_settings
        # 其次options
        # 最后global_settings
        # 前面的覆盖后面的
        if not self.configured:
            self._setup()
        self.options.update(options)
        global_settings = self.load_module(self.GLOBAL_SETTINGS)
        try:
            mod = self.load_module(self.settings_module)
        except ImportError as e:
            sys.stderr.write(e.message)
        else:
            for setting in dir(mod):
                setting_value = getattr(mod, setting)
                if setting.startswith("__"):
                    continue
                self.options[setting] = setting_value
            self.SETTINGS_MODULE = self.settings_module
        for setting in dir(global_settings):
            # if setting == setting.upper():
            #     setattr(self, setting, getattr(global_settings, setting))
            setattr(self, setting, getattr(global_settings, setting))
        for k, v in self.options.items():  # replace
            setattr(self, k, v)
        # patch when not regions config, ugly FIXME
        if not hasattr(self, "REGIONS"):
            region = self.REGION
            region.setdefault("name", "UNNAMED")
            self.REGIONS = {region["ID"]: region}

        self.configured = True

    def watch(self, key=None, callback=None):
        pass
        # if not self.configured:
        #     self._setup()
        # if not self.etcd:
        #     return
        # self.etcd.watch(key=key, callback=callback)
