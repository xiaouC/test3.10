#!/usr/bin/python
# coding: utf-8

import sys
import os
import shutil

if __name__ == '__main__':
    # windows should use ";" to seperate module paths
    current_dir = os.path.dirname(os.path.realpath(__file__))
    plugin_root = os.path.join(current_dir, '../frameworks/cocos2d-x/plugin')
    cocos_root = os.path.join(current_dir, '../frameworks/cocos2d-x')
    if sys.platform == 'win32':
        os.environ['NDK_MODULE_PATH'] = '%s;%s;%s/external;%s/cocos' % (plugin_root, cocos_root, cocos_root, cocos_root)
    else:
        os.environ['NDK_MODULE_PATH'] = '%s:%s:%s/external:%s/cocos' % (plugin_root, cocos_root, cocos_root, cocos_root)

    #
    old_dir = os.getcwd()
    os.chdir('../frameworks/runtime-src/proj.android')

    # 
    os.system('ndk-build APP_ABI="armeabi" NDK_DEBUG=0')

    os.chdir(old_dir)
