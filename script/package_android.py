#!/usr/bin/python
# coding: utf-8

import sys
import os
import shutil

if __name__ == '__main__':
    old_dir = os.getcwd()
    os.chdir('../frameworks/runtime-src/proj.android')

    if len(sys.argv) >= 2:
        os.system('ant %s'%sys.argv[1])
    else:
        os.system('ant release')

    os.chdir(old_dir)
