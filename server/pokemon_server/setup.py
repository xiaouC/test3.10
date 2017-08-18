#!/usr/bin/env python
from distutils.core import setup
from distutils.extension import Extension

ext_modules = [
    #  Extension("player.base",  ["player/c_player.c"])
    #, Extension("pet.c_pet",    ["pet/model.c"])
    Extension('player.c_player',   ['player/c_player.c'])
   ,Extension('pet.c_pet',         ['pet/c_pet.c'])
   ,Extension('faction.c_faction', ['faction/c_faction.c'])
   ,Extension('user.c_user',       ['user/c_user.c'])
   ,Extension('mail.c_mail',       ['mail/c_mail.c'])
   ,Extension('equip.c_equip',     ['equip/c_equip.c'])
   ,Extension('group.c_group',     ['group/c_group.c'])
   ,Extension('tower.c_floor',     ['tower/c_floor.c'])
]

import os
setup(
    name = 'engine',
    ext_modules = ext_modules
)
