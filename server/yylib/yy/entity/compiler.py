# coding: utf-8
'''
公式编译器
>>> def get_variable(name):
...     return {
...         'a': 2,
...         'b': 3,
...         'c': 1,
...     }[name]
>>> f = 'math.pow(math.ceil(a),b)+c+e'
>>> replace_var(f)
'math.pow(math.ceil(ctx("a")),ctx("b"))+ctx("c")+ctx("e")'
>>> compile(f)[0]
set(['a', 'c', 'b'])
>>> compile(f)[1](get_variable)
10.0
'''

import re

var_reg = re.compile(r'([^.\w_"\']|^)([a-zA-Z_][\w_]*)(?=[^.\(\w_]|$)')
keywords = ['if', 'else', 'or', 'and']
def replace_var(s):
    '''
    替换公式中的变量 var 成为 ctx("var")
    '''
    def fsub(g):
        name = g.group(2)
        if name in keywords:
            return '%s%s'%(g.group(1), g.group(2))
        else:
            return '%sctx("%s")'%(g.group(1), g.group(2))
    return var_reg.sub(fsub, s)

def find_var(s):
    var_set = set(i for _, i in var_reg.findall(s))
    return var_set - set(keywords)

def replace_var_for_mako(s):
    '''
    替换公式中的变量 var 成为 ctx("var")
    '''
    def fsub(g):
        name = g.group(2)
        if name in keywords:
            return '%s%s'%(g.group(1), g.group(2))
        else:
            return '%sself.%s'%(g.group(1), g.group(2))
    return var_reg.sub(fsub, s)

def compile(s):
    # clean
    s = s.strip().replace('\r\n', ' ').replace('\n', ' ')
    var_set = find_var(s)
    s = replace_var(s)
    s = 'lambda ctx: %s'%(s or None)
    import math
    from formulas import g_formulas
    return var_set, eval(s, {'__builtins__':None, 'fn': g_formulas, 'math': math}, {})

if __name__ == '__main__':
    import doctest
    doctest.testmod()
