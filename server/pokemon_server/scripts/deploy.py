# coding:utf-8
import sys
import ujson
import logging
logging.basicConfig(
    stream=sys.stdout, level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)
from fabric.operations import prompt
from fabric.operations import run
from fabric.api import env
from fabric.api import settings
from fabric.api import hide
from fabric.api import task
from fabric.contrib.files import upload_template
from fabric.colors import green
from pprint import pformat

from conf.etcd_config import EtcdConfig

ETCD_URL = "https://120.132.50.137:4001"


def noop(s):
    return s


def ensure_dir(dir):
    run("mkdir -p %s" % dir)


def home():
    with settings(hide("everything"), warn_only=True):
        return run("echo $HOME")


class Option(object):
    validate = noop

    def __init__(self, name, default, not_prompt=False):
        self.name = name
        self.default = default
        self._value = None
        self.not_prompt = not_prompt

    @property
    def value(self):
        if not self._value:
            return self.default
        return self._value

    @value.setter
    def value(self, value):
        self._value = value

    def prompt(self, default=None):
        if self.not_prompt:
            pass
        else:
            message = 'Input `%s`' % (self.name)
            if default is None:
                default = self.default
            if isinstance(default, basestring):
                default = default.encode("utf-8")
            self.value = prompt(
                message, default=default, validate=self.validate)


class IntOption(Option):
    validate = int


class StrOption(Option):
    validate = str


class Server(object):
    def __init__(self):
        self.options = []

    def add_options(self, *options):
        self.options.extend(options)

    def as_dict(self):
        result = {}
        # FIXME  {{

        def yield_names(names):
            result = []
            for name in names:
                result.append(name)
                yield result

        for option in self.options:
            bases = option.name.split(".")
            for names in yield_names(bases):
                __result = result
                for index, name in enumerate(names):
                    last = bool(index + 1 == len(bases))
                    if last:
                        __result[name] = option.value
                    else:
                        __result.setdefault(name, {})
                        __result = __result[name]
        # }}
        return result

    def prompt(self, **defaults):
        for option in self.options:
            default = defaults
            for i in option.name.split("."):
                default = default.get(i, {})
            option.prompt(default=default or None)

    def alter(self):
        try:
            info = self.info()
        except KeyError:
            info = {}
        self.prompt(**info)
        for k, v in self.as_dict().items():
            self.etcd.write(k, ujson.encode(v))


class SdkApp(Server):
    def __init__(self, sessionID):
        super(SdkApp, self).__init__()
        self.home = home()
        self.etcd = EtcdConfig(ETCD_URL, [sessionID])
        self.sessionID = sessionID
        self.add_options(
            StrOption("SDKAPP.host", ""),
            IntOption("SDKAPP.port", ""),
        )

    def info(self):
        info = self.as_dict()
        payload = self.etcd.info(recursive=False)
        info.update(**payload)
        return info

    def new(self):
        self.alter()
        payload = self.etcd.info(recursive=False)
        ensure_dir("%s/{data,log}" % payload["DIRECTORY"])
        upload_template(
            "scripts/templates/sdkapp.conf",
            "%s/service/conf.d/sdkapp%d.conf" % (self.home, self.sessionID),
            context=payload, use_jinja=True)
        return payload


class Gm(Server):
    def __init__(self, sessionID):
        super(Gm, self).__init__()
        self.home = home()
        self.etcd = EtcdConfig(ETCD_URL, [sessionID])
        self.sessionID = sessionID
        self.add_options(
            StrOption("PROXY.host", ""),
            IntOption("PROXY.port", ""),
        )

    def info(self):
        info = self.as_dict()
        payload = self.etcd.info(recursive=False)
        info.update(**payload)
        return info

    def new(self):
        self.alter()
        payload = self.etcd.info(recursive=False)
        ensure_dir("%s/{data,log}" % payload["DIRECTORY"])
        upload_template(
            "scripts/templates/gm_uwsgi.ini",
            payload["DIRECTORY"], context=payload, use_jinja=True)
        upload_template(
            "scripts/templates/gm.conf",
            "%s/service/conf.d/gm%d.conf" % (self.home, self.sessionID),
            context=payload, use_jinja=True)
        return payload


class Session(Server):
    def __init__(self, sessionID):
        super(Session, self).__init__()
        self.home = home()
        self.etcd = EtcdConfig(ETCD_URL, [sessionID])
        self.sessionID = sessionID
        self.add_options(
            IntOption("SESSION.ID", sessionID, not_prompt=True),
            StrOption("SESSION.host", ''),
            IntOption("SESSION.port", int("2%d0" % sessionID)),
            StrOption("PYTHONPATH",   "%s/src/Release_120000" % self.home),
            StrOption("UID", env.user),
            StrOption("GID", env.user),
            StrOption("PYARGV", "--etcd=%s --servers=%d" % (
                ETCD_URL, sessionID)),
            StrOption("VIRTUALENV", "%s/env" % self.home),
            StrOption("DIRECTORY", "%s/servers/session%d" % (
                self.home, sessionID)),
            StrOption("REDISES.session", "redis://localhost:9999"),
            StrOption("REDISES.identity", "redis://localhost:9999"),
            StrOption("REDISES.user", "redis://localhost:9999"),
            StrOption("REDISES.entity", "redis://localhost:9999"),
            StrOption("REDISES.settings", "redis://localhost:9999"),
            StrOption("REDISES.index", "redis://localhost:9999"),
            StrOption("REDISES.giftkey", "redis://localhost:9999"),
            StrOption("REDISES.payment", "redis://localhost:9999"),
            StrOption("REDISES.friendfb", "redis://localhost:9999"),
            StrOption("ETCD", ETCD_URL),
        )

    def new(self):
        self.alter()
        payload = self.etcd.info(recursive=False)
        ensure_dir("%s/{data,log}" % payload["DIRECTORY"])
        upload_template(
            "scripts/templates/session_uwsgi.ini",
            payload["DIRECTORY"], context=payload, use_jinja=True)
        upload_template(
            "scripts/templates/session.conf",
            "%s/service/conf.d/session%d.conf" % (self.home, self.sessionID),
            context=payload, use_jinja=True)
        return payload

    def info(self):
        info = self.as_dict()
        payload = self.etcd.info(recursive=False)
        info.update(**payload)
        return info


class Region(Server):
    def __init__(self, servers):
        super(Region, self).__init__()
        self.home = home()
        self.sessionID, self.regionID = servers
        self.etcd = EtcdConfig(ETCD_URL, servers)
        self.add_options(
            IntOption("REGION.ID", self.regionID, not_prompt=True),
            StrOption("REGION.name", ""),
        )
        self.session = Session(self.sessionID)

    def info(self):
        info = self.as_dict()
        info.update(**self.session.info())
        payload = self.etcd.info(recursive=False)
        info.update(**payload)
        return info

    def new(self):
        self.alter()
        payload = self.etcd.info(recursive=False)
        return payload


class World(Server):
    def __init__(self, servers):
        super(World, self).__init__()
        self.home = home()
        self.sessionID, self.regionID, self.worldID = servers
        self.etcd = EtcdConfig(ETCD_URL, servers)
        self.add_options(
            StrOption("PYTHONPATH",   "%s/src/Release_120000" % self.home),
            StrOption("UID", env.user),
            StrOption("GID", env.user),
            StrOption("VIRTUALENV", "%s/env" % self.home),
            StrOption("DIRECTORY", "%s/servers/game%d" % (
                self.home, self.regionID)),
            IntOption("WORLD.ID", self.worldID, not_prompt=True),
            StrOption("WORLD.ip", ""),
            IntOption("WORLD.port", int("1%d%d" % (
                self.regionID, self.worldID))),
            StrOption("WORLD.managehost", "127.0.0.1"),
            IntOption("WORLD.manageport", int("2%d%d" % (
                self.regionID, self.worldID))),
            StrOption("WORLD.mode", ""),
            IntOption("WORLD.backdoorport", int("3%d%d" % (
                self.regionID, self.worldID))),
        )
        self.region = Region([self.sessionID, self.regionID])

    def info(self):
        info = self.as_dict()
        info.update(**self.region.info())
        payload = self.etcd.info(recursive=False)
        info.update(**payload)
        return info

    def new(self):
        self.alter()
        payload = self.etcd.info(recursive=False)
        ensure_dir("%s/{data,log}" % payload["DIRECTORY"])
        upload_template(
            "scripts/templates/game.conf",
            "%s/service/conf.d/game%d.%d.conf" % (
                self.home, self.regionID, self.worldID),
            context=payload, use_jinja=True)
        return payload


@task
def info_session(sessionID):
    sessionID = int(sessionID)
    session = Session(sessionID)
    info = session.info()
    logger.info(green("Session %d info:" % sessionID, bold=True))
    logger.info(green(pformat(info), bold=True))
    return info


@task
def new_session(sessionID):
    sessionID = int(sessionID)
    session = Session(sessionID)
    info = session.new()
    logger.info(green("New session %d info:" % sessionID, bold=True))
    logger.info(green(pformat(info), bold=True))
    return info


@task
def alter_session(sessionID):
    sessionID = int(sessionID)
    session = Session(sessionID)
    session.alter()
    info = session.info()
    logger.info(green("Session %d info:" % sessionID, bold=True))
    logger.info(green(pformat(info), bold=True))
    return info


@task
def info_region(*servers):
    servers = map(int, servers)
    region = Region(servers)
    info = region.info()
    logger.info(green("Region %r info:" % servers, bold=True))
    logger.info(green(pformat(info), bold=True))
    return info


@task
def new_region(*servers):
    servers = map(int, servers)
    region = Region(servers)
    info = region.new()
    logger.info(green("Region %r info:" % servers, bold=True))
    logger.info(green(pformat(info), bold=True))
    return info


@task
def alter_region(*servers):
    servers = map(int, servers)
    region = Region(servers)
    region.alter()
    info = region.info()
    logger.info(green("Region %r info:" % servers, bold=True))
    logger.info(green(pformat(info), bold=True))
    return info


@task
def info_gm(sessionID):
    sessionID = int(sessionID)
    gm = Gm(sessionID)
    info = gm.info()
    logger.info(green("Gm %d info:" % sessionID, bold=True))
    logger.info(green(pformat(info), bold=True))
    return info


@task
def new_gm(sessionID):
    sessionID = int(sessionID)
    gm = Gm(sessionID)
    info = gm.new()
    logger.info(green("New gm %d info:" % sessionID, bold=True))
    logger.info(green(pformat(info), bold=True))
    return info


@task
def alter_gm(sessionID):
    sessionID = int(sessionID)
    gm = Gm(sessionID)
    gm.alter()
    info = gm.info()
    logger.info(green("Session %d info:" % sessionID, bold=True))
    logger.info(green(pformat(info), bold=True))
    return info


@task
def info_sdkapp(sessionID):
    sessionID = int(sessionID)
    sdkapp = SdkApp(sessionID)
    info = sdkapp.info()
    logger.info(green("SdkApp %d info:" % sessionID, bold=True))
    logger.info(green(pformat(info), bold=True))
    return info


@task
def new_sdkapp(sessionID):
    sessionID = int(sessionID)
    sdkapp = SdkApp(sessionID)
    info = sdkapp.new()
    logger.info(green("New sdkapp %d info:" % sessionID, bold=True))
    logger.info(green(pformat(info), bold=True))
    return info


@task
def alter_sdkapp(sessionID):
    sessionID = int(sessionID)
    sdkapp = SdkApp(sessionID)
    sdkapp.alter()
    info = sdkapp.info()
    logger.info(green("SdkApp %d info:" % sessionID, bold=True))
    logger.info(green(pformat(info), bold=True))
    return info


@task
def info_world(*servers):
    servers = map(int, servers)
    world = World(servers)
    info = world.info()
    logger.info(green("World %r info:" % servers, bold=True))
    logger.info(green(pformat(info), bold=True))
    return info


@task
def new_world(*servers):
    servers = map(int, servers)
    world = World(servers)
    info = world.new()
    logger.info(green("World %r info:" % servers, bold=True))
    logger.info(green(pformat(info), bold=True))
    return info


@task
def alter_world(*servers):
    servers = map(int, servers)
    world = World(servers)
    world.alter()
    info = world.info()
    logger.info(green("World %r info:" % servers, bold=True))
    logger.info(green(pformat(info), bold=True))
    return info
