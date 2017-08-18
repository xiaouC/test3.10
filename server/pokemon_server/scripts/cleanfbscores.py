#coding:utf-8

from yy.utils import load_settings
load_settings()
import settings

pool = settings.REDISES['entity']
def main(entityID, fbID):
    cmds = []
    keys = pool.execute('hkeys', "fbscores_p{%d}"%entityID)
    for key in keys:
        if int(key) > fbID:
            cmds.append(['hdel', "fbscores_p{%d}"%entityID, key])
    print cmds
    pool.execute_pipeline(*cmds)        

if __name__ == '__main__':
    import sys
    main(int(sys.argv[1]), int(sys.argv[2]))
