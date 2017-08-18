#!/usr/bin/python
# coding: utf-8
import os
ROOT = 'data'

import xlrd
import csv

def smart_str(s):
    if isinstance(s, unicode):
        return s.encode('utf-8')

    if isinstance(s, float) and int(s)==s:
        return int(s)

    return s

def convert(f):
    print u'处理', f
    b = xlrd.open_workbook(f)
    for s in b.sheets():
        if not s.name.startswith('export-'):
            continue

        basename = s.name[7:]
        path = os.path.join(ROOT, basename+'.csv')
        bc = open(path, 'wb')
        bcw = csv.writer(bc, csv.excel, lineterminator='\n')

        #剔除策划使用列
        excludecol = []
        for col in range(s.ncols):
            v = s.cell_value(1,col)
            if isinstance(v, unicode) and ":" in v and ":" == v[0] :
                excludecol.append(col)

        #第一行给策划说明用，跳过读取
        for row in range(1,s.nrows):
            this_row = [smart_str(s.cell_value(row,col)) for col in range(s.ncols) if col not in excludecol ]
            bcw.writerow(this_row)
        print u'输出', path

def main(excel_dir):
    for f in os.listdir(excel_dir):
        if f.endswith('.xls'):
            convert(os.path.join(excel_dir, f))

if __name__ == '__main__':
    import sys
    if len(sys.argv)>1:
        main(sys.argv[1])
    else:
        main(u'../design/05_配置文档')
