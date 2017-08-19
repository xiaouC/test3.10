# coding: utf-8
import logging
logger = logging.getLogger('session')

def init():
    import settings
    settings.watch()

    import session.views  # NOQA

    import gevent
    from session.regions import run_world_reloader
    gevent.spawn(run_world_reloader)


try:
    from uwsgidecorators import postfork
except ImportError:
    import gevent.monkey
    gevent.monkey.patch_all()
    init()
else:
    init = postfork(init)

from .app import application

if __name__ == '__main__':
    import settings
    import gevent_profiler
    import signal
    from gevent.pywsgi import WSGIServer

    gevent_profiler.attach_on_signal(signum=signal.SIGUSR1, duration=30)
    gevent_profiler.set_stats_output('stats.txt')
    gevent_profiler.set_summary_output('summary.txt')
    gevent_profiler.set_trace_output('trace.txt')

    logger.info('listening %s:%d', settings.SESSION['host'], settings.SESSION['port'])
    WSGIServer((settings.SESSION['host'], settings.SESSION['port']), application).serve_forever()
