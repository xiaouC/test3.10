import re
import rtx
import sys
import getpass
import os.path
import paramiko
from datetime import datetime
from gevent import spawn, joinall, monkey
from socket import timeout


class ExceptionCatcher(object):
    buffer = ""
    lasttime = None
    catching = False
    pattern = re.compile(r'([\d\ \:\-]+)')
    splitline = "----------------------------------------\n"

    def catch_time(self, line):
        '''Catch last time at line.'''
        match = self.pattern.match(line)
        if match:
            s = match.groups()[0].strip()
            try:
                dt = datetime.strptime(s, "%Y-%m-%d %H:%M:%S")
                self.lasttime = dt
            except ValueError:
                pass

    def catch(self, line):
        '''Catch a Traceback block.'''
        if not line.endswith("\n"):
            line += '\n'
        if line.startswith("Traceback"):
            if self.catching and self.buffer:
                self.emit()
            self.catching = True
            self.buffer += line
        elif line.startswith("  "):
            if self.catching and self.buffer:
                self.buffer += line
        else:
            if self.catching and self.buffer:
                self.buffer += line
                self.emit()
            self.catch_time(line)

    def ignore(self):
        return "error: [Errno 32] Broken pipe" in self.buffer

    def emit(self):
        if not self.ignore():
            context = ''
            if self.lasttime:
                context += "%s\n" % self.lasttime
            context = self.splitline + context + self.buffer + self.splitline
            print >> sys.stderr, str(context)
            # rtx.send(context)
        self.buffer = ''
        self.catching = False


def load_config():
    config = paramiko.SSHConfig()
    fn = os.path.expanduser("~/.ssh/config")
    with open(fn, "r") as f:
        config.parse(f)
    return config

try:
    ssh_config = load_config()
except IOError:
    ssh_config = None
BUF_SIZE = 1024


def ssh(host, user=getpass.getuser()):
    """Make ssh connecion"""
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    if ssh_config:
        c = ssh_config.lookup(host)
    else:
        c = {"hostname": host}
    client.connect(c["hostname"], username=c.get("user", user))
    return client


def tailf(host, filename, user=None):
    catcher = ExceptionCatcher()
    while True:
        client = ssh(host, user)
        transport = client.get_transport()
        transport.set_keepalive(True)
        channel = transport.open_session()
        channel.settimeout(30)
        cmd = "tail -f %s" % filename
        channel.exec_command(cmd)
        while transport.is_active():
            left = ""
            try:
                buf = channel.recv(BUF_SIZE)
            except timeout:
                continue
            if len(buf) > 0:
                stream = left + buf
                EOL = stream.rfind("\n")
                if EOL != len(stream) - 1:
                    left = stream[EOL+1:]
                    stream = stream[:EOL]
                else:
                    left = ""
                for line in stream.splitlines():
                    print >> sys.stderr, line
                    catcher.catch(line)
        client.close()


def mtailf(host, filenames, user=None):
    if len(filenames) > 1:
        monkey.patch_all()
        threads = [spawn(tailf, host, f, user=user) for f in filenames]
        joinall(threads)
    else:
        tailf(host, filenames[0], user=user)


def test_cacher(filenames):
    def t(f):
        catcher = ExceptionCatcher()
        with open(f, 'r') as fp:
            for l in fp:
                catcher.catch(l)

    threads = [spawn(t, f) for f in filenames]
    joinall(threads)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--files', nargs='+', type=str, required=True)
    parser.add_argument('-H', '--host', required=True, type=str)
    parser.add_argument("-u", '--user', type=str)
    args = parser.parse_args()
    mtailf(args.host, args.files, user=args.user)
