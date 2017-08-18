# coding: utf-8
import logging
logger = logging.getLogger('gm')


def check_configs():
    import re
    import os
    import logging
    from common import ConfigFiles
    logger = logging.getLogger('config')
    pattern = re.compile("region([0-9]{3})")
    for d in os.walk("data").next()[1]:
        match = pattern.match(d)
        if not match:
            continue
        config_files = ConfigFiles(match.groups()[0])
        path = os.path.join("data", d)
        logger.info("Config check %s" % path)
        config_files.check_files(path)
    logger.info("Config check success")


def init():
    import settings
    settings.watch()

    import gm.app

    import gevent
    from session.regions import run_region_reloader
    gevent.spawn(run_region_reloader)


try:
    from uwsgidecorators import postfork, uwsgi
except ImportError:
    import gevent.monkey
    gevent.monkey.patch_all()
    init()
    check_configs()
else:
    @postfork
    def redump_every_config():
        if uwsgi.is_locked():
            return
        uwsgi.lock()
        check_configs()
        uwsgi.unlock()

    init = postfork(init)


from .init_app import application


if __name__ == '__main__':
    import settings
    PROXY = settings.PROXY
    from gevent.pywsgi import WSGIServer
    logger.info('listening {}:{}'.format(PROXY['host'], PROXY['port']))
    WSGIServer((PROXY['host'], PROXY['port']), application).serve_forever()
