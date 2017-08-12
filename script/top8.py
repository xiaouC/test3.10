#!/usr/bin/env python
# coding=utf-8

import os, sys
from PIL import Image
import csv

dirs = [ '../res' ]
ignore_files = set( ['common.png', 'common_2.png', 'new_hall.png', 'Girl_tex.png'] )


# 转换文件 
def convert(filename):
    # 判断文件是否需要忽略
    if os.path.basename(filename) in ignore_files:
        return

    print("convert file name ", filename)

    img = Image.open(filename)
    img.load()

    # 文件已经是 P8
    if img.mode == "P":
        return

    # 执行转换 
    cmd = 'pngquant %s --force --ext  ".png" %s'%(filename, '> /dev/null' if os.name != 'nt' else '> $null')
    os.system(cmd)


# 转换目录
def convert_dir(dir):
    print 'convert_dir : ', dir
    for root, sub_dirs, files in os.walk(dir, followlinks = True):
        for f in files:
            if f.endswith('.png') or f.endswith('.PNG'):
                convert(os.path.join(root, f))


def rm_unused_p8_dir(dir):
    for root, sub_dirs, files in os.walk(dir, followlinks = True):
        for f in files:
            if f.endswith('.p8'):
                temp_file = f[:-3]

                # 如果这个 p8 对应的原文件已经不存在了，删除
                if not os.path.exists(os.path.join(root, temp_file)):
                    os.system('rm %s'%os.path.join(root,f))

                # 如果这个 p8 对应的原文件不需要压缩的话，删除
                if os.path.basename( temp_file ) in ignore_files:
                    os.system('rm %s'%os.path.join(root, f))


# 文件md5
def file_md5_size(f):
    import md5
    c = open(f, 'rb').read()
    return md5.md5(c).hexdigest(), len(c)


# 是否是相同文件
def is_same_file(filename, files_md5):
    md5, size = file_md5_size(filename)
    if filename not in files_md5:
        print "files_md5[filename] is null ................... : ", filename 
        return False

    return files_md5[filename] == md5


# 写入md5
def write_file_md5(dirs):
    writer = csv.writer(file('filelist_p8','wb'))
    for dir in dirs :
        for root, sub_dirs, files in os.walk(dir, followlinks = True):
            for f in files:
                if f.endswith('.png') or f.endswith('.PNG'):
                    abs_filename = os.path.join(root, f)
                    md5, size = file_md5_size(abs_filename)

                    writer.writerow([abs_filename,md5,size])


if __name__ == '__main__':
    files_md5 = {}

    # 如果文件不存在，先创建该文件，写入文件md5
    if not os.path.isfile('filelist_p8'):
        write_file_md5(dirs)

        for dir in dirs :
            print 'directory :', dir

            convert_dir( dir )
    else:
        reader = csv.reader(file('filelist_p8','rb'))
        # 获得文件md5的集合 
        for name,md5,size in reader:
            files_md5[name] = md5

        for dir in dirs:
            print 'directory :', dir
            for root, sub_dirs, files in os.walk(dir, followlinks = True) :
                for f in files:
                    # 查找png后缀的文件 
                    if f.endswith( '.png' ) or f.endswith( '.PNG' ):
                        # 判断当前文件的 md5 和历史版本是否一致, 如果一致，则不执行转换 
                        if is_same_file(os.path.join(root, f), files_md5):
                            continue
                        
                        print 'new file ', f
                        convert(os.path.join(root, f))
  
    # 删掉已经没有引用的 p8
    for dir in dirs:
        rm_unused_p8_dir(dir)

    write_file_md5(dirs)

    print 'convert completed!'
