from yy.db.redismanager import create_pool
from yy.utils import convert_list_to_dict
from optparse import OptionParser

REGIONS_KEY = 'REGIONS'
WHITELIST_REGIONS_KEY = 'REGIONS_ENABLE_WHITELIST'

POOLS = {
    'app': 'redis://192.168.100.101:9105/2',
    'ios': 'redis://192.168.100.101:9105',
    'android': 'redis://192.168.100.101:9105/1',
}

SERVERS = {
    'app': [
        (200, "审核服"),
        (201, "第1区 三头六臂"),
        (202, "第2区 莲池重生"),
        (203, "第3区 忠义乾坤"),
        (204, "第4区 凤鸣岐山"),
        (205, "第5区 武王伐纣"),
        (206, "第6区 风起陈塘"),
        (207, "第7区 忠肝义胆"),
    ],
    'ios': [
        (499, "体验服 解甲休士"),
        (400, "第1区 洞天福地"),
        (401, "第2区 纵横驰骋"),
        (402, "第3区 骁勇善战"),
        (403, "第4区 兵强马壮"),
        (404, "第5区 坚甲厉兵"),
    ],
    'android': [
        (599, "八仙过海"),
        (500, "第1区 腾云驾雾"),
        (501, "第2区 呼风唤雨"),
        (502, "第3区 搬山移海"),
        (503, "第4区 撒豆成兵"),
        (504, "第5区 水潜土遁"),
        (505, "第6区 白日升天"),
        (506, "第7区 二仙传道"),
        (507, "第8区 鸿衣羽裳"),
    ],
}

DESC = {
    'app': dict(
        invisible=[200],
        whitelist=[200],

        max_visible=204,
        min_whitelist=205,
    ),
    'ios': dict(
        invisible=[499],
        whitelist=[499],

        max_visible=404,
        min_whitelist=405,
    ),
    'android': dict(
        invisible=[599],
        whitelist=[599],

        max_visible=505,
        min_whitelist=506,
    ),
}


def one(platform, dryrun=True):
    print 'process', platform, POOLS[platform], 'DRYRUN' if dryrun else ''
    if not dryrun:
        pool = create_pool(POOLS[platform])
    servers = SERVERS[platform]
    desc = DESC[platform]

    visible_servers = []
    for id, name in servers:
        if id in desc['invisible']:
            continue
        elif id > desc['max_visible']:
            continue
        visible_servers.append(id)
        visible_servers.append(name)

    cmds = [
        ('del', REGIONS_KEY),
        ('hmset', REGIONS_KEY) + tuple(visible_servers),
    ]

    if not dryrun:
        pool.execute_pipeline(*cmds)
    else:
        print cmds

    # whitelist
    whitelist_servers = []
    for id, name in servers:
        if id in desc['whitelist']:
            whitelist_servers.append(id)
        elif id >= desc['min_whitelist']:
            whitelist_servers.append(id)
    cmds = [
        ('del', WHITELIST_REGIONS_KEY),
        ('sadd', WHITELIST_REGIONS_KEY) + tuple(whitelist_servers),
    ]

    if not dryrun:
        pool.execute_pipeline(*cmds)
    else:
        print cmds


def view(platform):
    pool = create_pool(POOLS[platform])
    print convert_list_to_dict(pool.execute('hgetall', REGIONS_KEY))
    print convert_list_to_dict(pool.execute('smembers', WHITELIST_REGIONS_KEY))


parser = OptionParser()
parser.add_option("-p", "--platform", dest="platform", type="string",
                  help="指定平台(app|ios|android)，默认全平台", metavar="PLATFORM")
parser.add_option("-n", "--dryrun", dest="dryrun", action="store_true",
                  help="dryrun")
parser.add_option("-l", "--list", dest="list", action="store_true",
                  help="list current server config")

if __name__ == '__main__':
    options, args = parser.parse_args()
    if options.list:
        if options.platform:
            view(options.platform)
        else:
            for platform in POOLS.keys():
                view(platform)
    else:
        if options.platform:
            one(options.platform, options.dryrun)
        else:
            for platform in POOLS.keys():
                one(platform, options.dryrun)
                print
