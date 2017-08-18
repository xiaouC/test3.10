#!/usr/bin/env python
from distutils.core import setup
from distutils.extension import Extension

ext_modules = [ Extension("yy.rpc.http.http", ["yy/rpc/http/http.c"])
              , Extension("yy.rpc.http.session", ["yy/rpc/http/session.c"])
              , Extension("yy.cutils", ["yy/cutils.c"])]
setup(
    name = 'yylib',
    version = '1.0.11',
    install_requires = ('bitarray >= 0.8.1',),
    packages = ['yy',
                'yy.config',
                'yy.cron',
                'yy.db',
                'yy.db.redis_scripts',
                'yy.entity',
                'yy.entity.storage',
                'yy.message',
                'yy.ranking',
                'yy.rpc',
                'yy.rpc.http',
                'yy.utils',
               ],
    package_data = {'yy.entity': ['entity_tpl.mako'],
                    'yy.db.redis_scripts': ['*.lua']
                   },
    ext_modules = ext_modules,
)
