#coding:utf-8
import os, json, urllib

def get_player_top(host, port):
    cmd = "http://{host}:{port}/player_top_ten".format(host=host, port=port)
    rsp = json.loads(urllib.urlopen(cmd).read())
    return rsp['rows']

mapping = {
    1:(1000, 2000000, '第1名'),
}
for i in range(2, 5 + 1):
    mapping[i] = (500, 1000000, '第2-5名')
for i in range(6, 10 + 1):     
    mapping[i] = (300, 500000, '第6-10名')
for i in range(11, 100 + 1):
    mapping[i] = (300, 300000, '第11-100名')
for i in range(101, 1000 + 1):
    mapping[i] = (100, 100000, '第101-1000名')

def give(host, port):
    data = get_player_top(host, port)
    for rank, (entityID, _, _, _, _) in enumerate(data, 1):
        if rank not in mapping:
            continue
        gold, money, desc = mapping[rank]
        cmd = "curl -d'title={title}&entityID={entityID}&gold={gold}&money={money}' http://{host}:{port}/add_mail/{entityID}"
        title = '冲级大赛 ' + desc
        print os.system(cmd.format(host=host, port=port, entityID=entityID, gold=gold, money=money, title=title))

if __name__ == '__main__':
    import sys
    host, port = sys.argv[1], sys.argv[2]
    give(host, port)
