# coding:utf-8
import urllib
from protocol.poem_pb import XXXX

def main():
    url = "http://xxxxx:xxx/msgid"
    f = urllib.urlopen(url)
    data = f.read()
    if data:
        req = XXX()
        req.ParseFromString(data)
        # send rtx
    return 
