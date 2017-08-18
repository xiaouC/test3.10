
#coding:utf-8

from yy.utils import load_settings
load_settings()
import settings
import ujson

pool = settings.REDISES['entity']
keys = pool.execute('keys', 'p{*}')
cmds = []
for key in keys:
    pets = ujson.loads(pool.execute('hget', key, 'petset'))
    cp_pets = list(pets)
    for pet in cp_pets:
        ex = pool.execute('EXISTS', "t{%d}"%pet)
        if not ex:
            print 'not ex', pet, key
            pets.remove(pet)
    if len(pets) != len(cp_pets):
        cmds.append(["hset", key, "petset", ujson.dumps(pets)])
print cmds
print pool.execute_pipeline(*cmds)    
