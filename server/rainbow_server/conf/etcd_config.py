"""
/NATAKU/
/NATAKU/SESSION100/
/NATAKU/SESSION100/REGION100/
/NATAKU/SESSION100/REGION100/INFO
/NATAKU/SESSION100/REGION100/STATUS
/NATAKU/SESSION100/REGION100/WORLD100/
/NATAKU/SESSION100/REGION100/WORLD100/INFO
"""
"""
{u'REGIONS': {100: {u'ID': 100}, 101: {u'ID': 101}},
 u'SESSION': {u'ID': 0,
  u'backdoor': [u'127.0.0.1', 3502],
  u'client': [u'0.0.0.0', 29000],
  u'http': [u'0.0.0.0', 21014],
  u'sdk': [u'0.0.0.0', 3501],
  u'world': [u'127.0.0.1', 3500]},
 u'WORLDS': {1: {u'ID': 100,
   u'backdoorport': 4253,
   u'ip': u'192.168.0.39',
   u'managehost': u'127.0.0.1',
   u'manageport': 11021,
   u'mode': u'NORMAL',
   u'port': 5250}}}

{
    SESSION : {
        ID: 100
        backdoor: (127.0.0.1, 3502),
        client: (0.0.0.0, 29000),
        http: (0.0.0.0, 21014),
        sdk: (0.0.0.0, 3501),
        REGIONS: {
            100 : {
                ID: 100
                WORLDS: {
                    100: {

                    }
                }
            }
        }
    }
}
"""
import logging
logger = logging.getLogger('etcd')

import os
import re
import ssl
import etcd
import json
import argparse
from os.path import split as pathsplit
from urllib3.util import parse_url
from gevent import kill
from gevent import sleep
from gevent import Greenlet


def split_letters(string):
    return re.sub(r"\d", "", string), int(re.sub(r"[A-Za-z]", "", string))

CA_PATH = os.path.join(os.path.split(os.path.abspath(__file__))[0], 'certs')


class EtcdConfig(object):

    def __init__(self, endpoint, servers):
        url = parse_url(endpoint)
        self.client = etcd.Client(
            host=url.host, port=url.port, protocol="https",
            cert=(
                "%s/client.crt" % CA_PATH,
                "%s/client.key.insecure" % CA_PATH),
            ca_cert="%s/ca.crt" % CA_PATH)
        self.parser = argparse.ArgumentParser()
        self.parser.add_argument(
            "-s", "--servers",  nargs="+", type=int, required=True)
        raws = ["--servers"] + map(str, servers or [])
        self.args = self.parser.parse_args(raws)
        self.keys = []
        servers = []
        for index, server in enumerate(self.args.servers[:3]):
            if index == 0:  # SESSION
                key = "/NATAKU/SESSION{0}"
            elif index == 1:  # REGION
                key = "/NATAKU/SESSION{0}/REGION{1}"
            elif index == 2:  # WORLD
                key = "/NATAKU/SESSION{0}/REGION{1}/WORLD{2}"
            servers.append(server)
            key = key.format(*servers)
            self.keys.append(key)
        self.key = self.keys[0]
        self.watcher = None

    def get(self, key, **kwargs):
        info = {}
        recursive = kwargs.get("recursive", False)
        rsp = self.client.read(key, **kwargs)
        for child in rsp.get_subtree():
            if pathsplit(child.key)[0] != key:  # skip children's attrs
                continue
            if recursive and child.dir:  # sub children, make an dict
                for c in child.children:
                    root, attr = pathsplit(c.key)
                    basename, id = split_letters(pathsplit(root)[1])
                    if root == child.key and basename == attr:
                        # only match the main info
                        attrs = "%sS" % attr
                        info.setdefault(attrs, {})[id] = json.loads(c.value)
                continue
            else:
                try:
                    value = json.loads(child.value)
                except TypeError:
                    if recursive:
                        raise TypeError("%s is a directory" % child.key)
                    else:
                        continue
                _, attr = pathsplit(child.key)
                info[attr] = value
        return info

    def info(self, recursive=True):
        info = {}
        for key in self.keys:
            rs = self.get(key, recursive=recursive)
            info.update(rs)
        return info

    def write(self, key, value, **kwargs):
        key = "/".join([self.keys[-1], key])
        return self.client.write(key, value, **kwargs)

    def watch(self, key=None, callback=None):
        key = key or self.key
        assert key, "key is %r" % key
        if self.watcher:
            kill(self.watcher)
        self.watcher = Greenlet.spawn(self.watching, key, callback)
        self.watcher.start()

    def watching(self, key, callback):
        logger.info('start watching')
        while True:
            try:
                self.client.read(
                    key, wait=True, recursive=True)
            except (etcd.EtcdException, ssl.SSLError):
                continue
            callback()
            sleep(1)
