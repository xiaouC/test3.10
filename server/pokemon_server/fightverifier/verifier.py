import os, os.path
from zipfile import ZipFile
from lupa import LuaRuntime


def require_configs(rt, root):
    d = os.path.join(root, 'config')
    for f in os.listdir(d):
        if f.endswith('.lua') and f.startswith('C_'):
            rt.require('config.%s' % f[:-4])


def get_zip_loader(rt, f):

    zf = ZipFile(f)

    def zip_loader(filename):
        content = zf.open(filename.replace('.', '/')+'.lua', 'r').read()
        rt.execute(content)
        return 1

    return zip_loader


#def set_loader(rt, cb):
#    rt.eval('function(loader) table.insert(package.loaders, loader end')(cb)


def new_runtime():
    rt = LuaRuntime()

    lua_root = os.path.join(os.path.dirname(__file__), 'lua')

    path = os.path.join(lua_root, '?.lua')
    rt.eval("function(path) package.path = package.path .. ';' .. path end")(path)
    #rt.require('utils.common')
    rt.require('win.Fight.verify_manager')
    require_configs(rt, lua_root)

    reg_proto = rt.eval('protobuf.register')
    reg_proto(open(os.path.join(lua_root, 'config/poem.pb'), 'rb').read())
    reg_proto(open(os.path.join(lua_root, 'config/config.pb'), 'rb').read())

    #zip_loader = get_zip_loader(rt, '/tmp/test.zip')
    #set_loader(rt, zip_loader)
    #rt.require('test.xxx')

    return rt


def verify(rt, s):
    result = rt.eval('verifyFightPlaybackWithData')(s)
    return result


if __name__ == '__main__':
    import sys
    rt = new_runtime()
    print verify(rt, open(sys.argv[1], 'rb').read())
