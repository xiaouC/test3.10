# coding:utf-8
import os
import logging
logger = logging.getLogger('world')

import gevent
from gevent import Greenlet, socket, sleep, joinall, pool, monkey
monkey.patch_all()
logger.info("patch_all ok")

import sys
import signal
import urllib3
import traceback
import settings

from sentry import SentryClient

from yy.message.reader import MessageReader
from yy.message.asyncsocket import async_send_socket
from yy.message.exceptions import ConnectionClosed, CloseServer

from session.regions import run_region_reloader, reload_regions, add_world, update_world, del_world

region_reloader_thread = None


def start_region_reloader():
    global region_reloader_thread
    region_reloader_thread = gevent.spawn(run_region_reloader)
start_region_reloader()


sentry = SentryClient()


class WorldServer(object):

    def __init__(self):
        self.pulse = 3000  # milliseconds
        self.interval = self.pulse + 5000
        self.started = False
        reload_worlds()
        self.join_worlds()
        gevent.signal(signal.SIGTERM, self.clean_quit)
        gevent.signal(signal.SIGINT, self.clean_quit)

    def join_worlds(self):
        from session.regions import g_worlds
        # 检查是否跟已存在的world重复了
        assert settings.WORLD['ID'] not in g_worlds, "Duplicate world {}".format(settings.WORLD['ID'])
        add_world(settings.WORLD['ID'], self.interval, dict(settings.WORLD))
        s = ','.join(['<%d %s:%d>' % (i.id, i.ip, i.port) for i in g_worlds.values()])
        logger.info('current worlds {}'.format(s))

    def ping_proxy(self):
        import settings as st
        from gm.proxy import proxy
        while True:
            try:
                proxy.ping()
            except urllib3.exceptions.MaxRetryError:
                logger.info("Can't connect proxy {host}:{port}".format(**st.PROXY))
            else:
                logger.info("Connected proxy {host}:{port}".format(**st.PROXY))
                from config.configs import get_registereds
                from yy.config.fields import ValidationError
                from common import ConfigFiles
                config_files = ConfigFiles(st.REGION['ID'])
                try:
                    config_files.load_configs(get_registereds(), st.CONFIG_FILE_PATH)
                except ValidationError as e:
                    print e.message.encode("utf-8")
                    raise e
                logger.info('Config loaded %s', st.CONFIG_FILE_PATH)
                break
            sleep(1)

    def heart_beat(self):
        from player.manager import g_playerManager
        while True:
            try:
                setted = update_world(settings.WORLD["ID"], self.interval, online=g_playerManager.count())
                if not setted:
                    self.join_worlds()
            except:
                logger.exception('heart beat')
            sleep(self.pulse / float(1000))

    def clean_settings(self):
        del_world(settings.WORLD['ID'])

    def handle_client(self, sock, address):
        '处理单个客户端连接'
        from world.service import WorldService
        from player.manager import QuitPlayer
        logger.info('new connection')
        reader = MessageReader(sock, self)
        sock = async_send_socket(sock)
        service = WorldService(self, sock)
        try:
            for msgtype, body, _ in reader.read_message():
                rsp = service.rpccall(msgtype, body)
                if rsp is not None:
                    sock.async_send(rsp)
        except (QuitPlayer, CloseServer):
            logger.error('client disconnected kicked out')
            service.connection_closed()
        except (ConnectionClosed, socket.error):
            # 网络断开
            service.connection_closed()
            logger.error('client disconnected')
        except:
            # 异常退出
            traceback.print_exc()
            sentry.send(sys.exc_info())
            service.connection_closed()
            logger.error('client disconnected exception')
        finally:
            # cleanup
            sock.async_close()

    def run(self):
        from gevent.server import StreamServer
        from gevent.pywsgi import WSGIServer
        from gevent.backdoor import BackdoorServer
        import gm.app  # NOQA
        from gm.init_app import application
        import settings as st
        # wait for proxy
        self.ping_proxy()
        threads = []
        logger.info('listening 0.0.0.0:%d', st.WORLD['port'])
        self.mainServer = StreamServer(('0.0.0.0', st.WORLD['port']), self.handle_client)
        threads.append(Greenlet.spawn(self.mainServer.serve_forever))
        logger.info('listening %s:%d', st.WORLD['managehost'], st.WORLD['manageport'])
        threads.append(Greenlet.spawn(WSGIServer((st.WORLD['managehost'], st.WORLD['manageport']), application, spawn=pool.Pool(10)).serve_forever))
        if os.environ.get("DOCKER_MANAGEHOST"):
            backdoorhost = "0.0.0.0"
        else:
            backdoorhost = "127.0.0.1"
        logger.info('listening %s:%d', backdoorhost, st.WORLD['backdoorport'])
        threads.append(Greenlet.spawn(BackdoorServer((backdoorhost, st.WORLD['backdoorport'])).serve_forever))
        # start cron thread
        import cron_settings  # NOQA
        threads.append(Greenlet.spawn(self.heart_beat))
        joinall(threads)

    def clean_quit(self):
        '''
        1、关闭监听端口
        2、清理玩家socket和数据
        '''
        from player.manager import g_playerManager
        try:
            if self.started:
                self.mainServer.stop()
            for entityID in g_playerManager.peers.keys():
                g_playerManager.kick_player(entityID)
        finally:
            self.clean_settings()
        sys.exit(0)


def log_traceback(signum, frame):
    logger.error(traceback.format_stack(frame))


if __name__ == '__main__':
    g_worldServer = WorldServer()
    import gevent_profiler

    signal.signal(signal.SIGUSR2, log_traceback)

    settings.watch()
    # import signal
    # gevent_profiler.attach_on_signal(signum=signal.SIGUSR1, duration=60)
    gevent_profiler.set_stats_output('stats.txt')
    gevent_profiler.set_summary_output('summary.txt')
    gevent_profiler.set_trace_output('trace.txt')
    g_worldServer.run()
