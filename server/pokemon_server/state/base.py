# coding:utf-8
import time
from gevent import kill
from gevent import sleep
from gevent import Greenlet
import logging
logger = logging.getLogger("state")


class StopStateException(Exception):
    pass


class Foresee(object):
    """提前知道生成器是否有下一个迭代子"""

    def __init__(self, it):
        self.it = iter(it)
        self._hasnext = None

    def __iter__(self):
        return self

    def next(self):
        if self._hasnext:
            result = self._thenext
        else:
            result = next(self.it)
        self._hasnext = None
        return result

    def hasnext(self):
        if self._hasnext is None:
            try:
                self._thenext = next(self.it)
            except StopIteration:
                self._hasnext = False
            else:
                self._hasnext = True
        return self._hasnext


class State(object):

    def __init__(self, obj):
        self.obj = obj

    def info(self, action):
        logger.info("%s %s", self.obj.__class__.__name__, action)

    def enter(self):
        raise NotImplementedError

    def execute(self):
        raise NotImplementedError

    def exit(self):
        raise NotImplementedError


class StartState(State):

    def enter(self):
        self.info("enter start")
        self.obj.enter_start()

    def execute(self):
        self.info("execute start")
        self.obj.execute_start()

    def exit(self):
        self.info("exit start")
        self.obj.exit_start()


class WaitState(State):

    def enter(self):
        self.info("enter wait")
        self.obj.enter_wait()

    def execute(self):
        self.info("execute wait")
        self.obj.execute_wait()

    def exit(self):
        self.info("exit wait")
        self.obj.exit_wait()


class StopState(State):

    def enter(self):
        self.info("enter stop")
        self.obj.enter_stop()

    def execute(self):
        self.info("execute stop")
        self.obj.execute_stop()

    def exit(self):
        self.info("exit stop")
        self.obj.exit_stop()


class StateObject(object):

    def __init__(self, wait_interval=0):
        self.wait_interval = wait_interval
        self.state = None
        self.current_loop = None
        self.loop = None

    def enter_start(self):
        pass

    def execute_start(self):
        pass

    def exit_start(self):
        pass

    def enter_wait(self):
        pass

    def execute_wait(self):
        pass

    def exit_wait(self):
        pass

    def enter_stop(self):
        pass

    def execute_stop(self):
        pass

    def exit_stop(self):
        pass

    def enter_state(self, state):
        if self.state:
            self.state.exit()
        self.state = state
        self.state.enter()
        self.state.execute()

    def get_loops(self):
        """
        return sorted [[starttime, endtime, current_loop], ...]
        """
        raise NotImplementedError

    def run(self):
        loops = self.get_loops()
        if hasattr(loops, "next"):
            loops = Foresee(loops)
            keys = True
            if not loops.hasnext():
                keys = False
        else:
            keys = list(loops)
        while keys:
            for k in loops:
                start, end, current_loop = k
                now = int(time.time())
                try:
                    if now >= start and now < end:  # 开启中
                        self.current_loop = current_loop
                        self.enter_state(StartState(self))
                        sleep(end - now)  # 休眠至等待
                        self.enter_state(WaitState(self))
                        sleep(self.wait_interval)  # 休眠至发奖
                        self.enter_state(StopState(self))
                    elif start > now:  # 即将开启
                        self.current_loop = current_loop
                        if self.state:
                            self.state.exit()
                        sleep(start - now)  # 休眠至开启
                        self.count = 0
                        if hasattr(loops, "next"):
                            loops = Foresee(self.get_loops())
                        else:
                            loops = self.get_loops()
                        break
                    elif end <= now:  # 过期的下次不再判断
                        try:
                            keys.remove(k)
                        except ValueError:
                            pass
                        except AttributeError:
                            pass
                except StopStateException:
                    self.stop()

    def start(self):
        self.stop()
        self.loop = Greenlet.spawn(self.run)
        self.loop.start()

    def stop(self):
        self.state = None
        if self.loop:
            kill(self.loop)
