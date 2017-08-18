# coding:utf-8
import os
import sys
import time
import errno
import signal
import traceback
import logging
logging.basicConfig(level=logging.INFO)


class HaltServer(BaseException):
    def __init__(self, reason, exit_status=1):
        self.reason = reason
        self.exit_status = exit_status

    def __str__(self):
        return "<HaltServer %r %d>" % (self.reason, self.exit_status)


class Arbiter(object):

    WORKERS = {}
    WORK_BOOT_ERROR = 3

    SIG_QUEUE = []
    SIGNALS = [
        getattr(signal, "SIG%s" % x) for x in "QUIT TERM INT CLD".split()]
    SIG_NAMES = dict(
        (getattr(signal, name), name[3:].lower()) for name in dir(signal)
        if name[:3] == "SIG" and name[3] != "_"
    )

    log = logging.getLogger("region")

    def __init__(self, worker_id_list, worker_class, ip=None):
        self.worker_id_list = worker_id_list
        self.graceful_timeout = 1
        self.worker_class = worker_class
        self.ip = ip

    def init_signal(self):
        [signal.signal(s, self.signal) for s in self.SIGNALS]
        # signal.signal(signal.SIGCHLD, self.handle_chld)

    def signal(self, sig, frame):
        if len(self.SIG_QUEUE) < 5:
            self.SIG_QUEUE.append(sig)

    def handle_cld(self):
        self.reap_workers()

    def handle_term(self):
        raise StopIteration

    def handle_int(self):
        self.stop(False)
        raise StopIteration

    def handle_quit(self):
        self.stop(False)
        raise StopIteration

    def reap_workers(self):
        try:
            while True:
                wpid, status = os.waitpid(-1, os.WNOHANG)
                if not wpid:
                    break
                exitcode = status >> 8
                if exitcode == self.WORK_BOOT_ERROR:
                    reason = "Worker failed to boot."
                    raise HaltServer(reason, self.WORK_BOOT_ERROR)
                self.WORKERS.pop(wpid, None)
        except OSError as e:
            if e.errno != errno.ECHILD:
                raise

    def start(self):
        self.pid = os.getpid()
        self.init_signal()

    def run(self):
        self.start()
        self.manage_workers()
        while True:
            try:
                sig = self.SIG_QUEUE.pop(0) if len(self.SIG_QUEUE) else None
                if sig:
                    if sig not in self.SIG_NAMES:
                        self.log.warn("Ignoring unknown signal: %s", sig)
                        continue
                    signame = self.SIG_NAMES[sig]
                    handler = getattr(self, "handle_%s" % signame, None)
                    if not handler:
                        self.log.warn("Unhandled signal: %s", signame)
                        continue
                    self.log.info("Handling signal: %s", signame)
                    handler()
            except StopIteration:
                self.halt()
            except KeyboardInterrupt:
                self.halt()
            except HaltServer as e:
                self.halt(reason=e.reason, exit_status=e.exit_status)
            except SystemExit:
                raise
            except Exception:
                self.log.info(
                    "Unhandled exception in main loop:\n%s",
                    traceback.format_exc())
                self.stop(False)
                sys.exit(-1)

    def halt(self, reason=None, exit_status=0):
        self.stop()
        if reason is not None:
            self.log.error("Reason: %s", reason)
        sys.exit(exit_status)

    def stop(self, graceful=True):
        sig = signal.SIGTERM
        if not graceful:
            sig = signal.SIGQUIT
        limit = time.time() + self.graceful_timeout
        while self.WORKERS and time.time() < limit:
            self.kill_workers(sig)
            time.sleep(0.1)
        self.kill_workers(signal.SIGKILL)

    def manage_workers(self):
        for w in self.worker_id_list:
            self.spawn_worker(w)
            time.sleep(0.1)
        # assert len(self.worker_id_list) == len(self.WORKERS)

    def spawn_worker(self, worker_id):
        worker = self.worker_class(worker_id, ip=self.ip)
        pid = os.fork()
        if pid != 0:
            self.WORKERS[pid] = worker
            return pid
        # Process Child
        # worker_pid = os.getpid()
        try:
            worker.init_process()
            sys.exit(0)
        except SystemExit:
            raise
        except:
            self.log.error(
                "Unhanlded exception in worker process:\n%s",
                traceback.format_exc())
            sys.exit(self.WORK_BOOT_ERROR)

    def kill_workers(self, sig):
        worker_pids = list(self.WORKERS.keys())
        for pid in worker_pids:
            self.kill_worker(pid, sig)

    def kill_worker(self, pid, sig):
        try:
            os.kill(pid, sig)
        except OSError as e:
            if e.errno == errno.ESRCH:
                return
            raise

if __name__ == "__main__":
    print Arbiter([100, 101], None)
