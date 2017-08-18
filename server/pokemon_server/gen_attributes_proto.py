#!/usr/bin/python
# coding: utf-8
import sys
from player.define import player_fields
from pet.define import pet_fields
from equip.define import equip_fields
from itertools import count

def diff_fields(fields1, fields2):
    return fields1.difference(fields2)

def to_proto(output=None):
    type_to_proto = {
        'cycle': 'int32',
        'integer': 'int32',
        'boolean': 'bool',
        'string': 'string',
    }
    if output:
        fp = open(output, 'w')
    else:
        fp = sys.stdout
    print >>fp, 'package poem;'
    print >>fp, 'option optimize_for = LITE_RUNTIME;'
    print >>fp, '// 属性集合'
    print >>fp, 'message Property {'
    attrs = {k:v for k, v in pet_fields.items() if v.sync}
    attrs.update({k:v for k, v in player_fields.items() if v.sync})
    diff = diff_fields(set({k:v for k, v in equip_fields.items() if v.sync}), attrs.keys())
    diff = sorted(diff, key=lambda s:equip_fields[s].id)
    anti_attrs = {v.id:k for k, v in attrs.items()}
    for d in diff:
        for i in count(1):
            if i not in anti_attrs:
                equip_fields[d].id = i
                attrs[d] = equip_fields[d]
                anti_attrs[i] = d
                break
    for each in sorted(attrs.values(), key=lambda s:s.id):
        s = '    optional %s %s = %d' % (type_to_proto[each.type], each.name, each.id)
        if each.default:
            s +=  ' [default=%s]'%repr(each.default).lower()
        s += '; // %s' % each.description
        print >>fp, s
    print >>fp, '}'

if __name__ == '__main__':
    to_proto()
