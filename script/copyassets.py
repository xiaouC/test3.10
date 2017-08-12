#!/usr/bin/python
# coding: utf-8

import sys
import os
import shutil

def copyto(f, target):
    d = os.path.dirname(target)
    if not os.path.exists(d):
        os.makedirs(d)

    shutil.copyfile(f, target)


copy_game_ids = [ '20000053', ]

def is_valid_dir(r, platform=None):
    if '.svn' in r:
        return False

    if '.git' in r:
        return False

    if r.startswith('game_res'):
        rs = r.split('/')
        if len(rs) > 1 and rs[1].isdigit():
            game_id = rs[1]
            if game_id in copy_game_ids:
                return True

        return False

    if r.startswith('app/platform/game'):
        rs = r.split('/')

        if rs[2] == 'gamerecord':
            return False

        if rs[2] == 'game' and len(rs) > 3 and rs[3].isdigit():
            game_id = rs[3]
            if game_id in copy_game_ids:
                return True

            return False

    return True


ignore_files = set(['Thumbs.db', 'Thumbs.db:encryptable', 'gmon.out', 'UserDefault.xml', ])
ignore_exts = set(['.dll', '.exe', '.a', '.fla', '.animxml', '.orig', '.mp4', '.py', '.pyc', '.pyo', '.bat', '.txt' ])
def is_valid_file(f, r):
    basename = os.path.basename(f)

    if basename.startswith('.'):
        return False

    if basename in ignore_files:
        return False

    if basename.startswith('callgrind'):
        return False

    ext = os.path.splitext(basename)[-1]
    if ext in ignore_exts:
        return False

    return True


def copy_dir(src_dir, dest_dir):
    for r, dirs, files in os.walk(src_dir, followlinks=True):
        r = os.path.relpath(r, src_dir)
        if r=='.':
            r = ''

        r = r.replace('\\', '/')
        if not is_valid_dir(r):
            continue

        for f in files:
            url = os.path.join(r, f)
            if not is_valid_file(f, r):
                continue

            url = url.replace('\\', '/')
            ipath = os.path.join(src_dir, url)
            opath = os.path.join(dest_dir, url)

            print '==================================================='
            print 'ipath : ', ipath
            print 'opath : ', opath
            copyto(ipath, opath)


if __name__ == '__main__':
    os.system('rm -r ../frameworks/runtime-src/proj.android/assets/src')
    os.system('rm -r ../frameworks/runtime-src/proj.android/assets/res')

    copy_dir('../src', '../frameworks/runtime-src/proj.android/assets/src')
    copy_dir('../res', '../frameworks/runtime-src/proj.android/assets/res')
