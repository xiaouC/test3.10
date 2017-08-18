#!/usr/bin/python
# coding: utf-8
import os
from datetime import datetime
ROOT = ''
import settings
pool = settings.REDISES["index"]
from giftkey import gen_key

import xlrd


def smart_str(s):
    if isinstance(s, unicode):
        return s.encode('utf-8').strip(" ")

    if isinstance(s, float) and int(s) == s:
        return int(s)

    return s


def main(excel_dir):
    for f in os.listdir(excel_dir):
        if (f.endswith('.xlsx') or f.endswith(".xls"))\
                and not f.startswith("~$"):
            convert(os.path.join(excel_dir, f))


def convert(f):
    print '处理', f
    log = open("%s %s.log" % (f, datetime.today()), "w")
    b = xlrd.open_workbook(f)
    for s in b.sheets():
        # 第一行是表头
        header = []
        for col in range(s.ncols):
            header.append(smart_str(s.cell_value(0, col)))
        if not header:
            continue
        if header[0] != "礼包码":
            continue
        if header[1] != "ID":
            continue
        rows = []
        for r in range(1, s.nrows):
            row = []
            for c in range(s.ncols):
                row.append(smart_str(s.cell_value(r, c)))
            rows.append(row)
        count = 0
        for row in rows:
            info = dict(zip(header, row))
            key = info["礼包码"]
            itemID = info["ID"]
            channels = info.get("渠道号")
            key = gen_key(itemID, key, channels=channels)
            if key:
                key = key[0]
            print >> log, key
            count += 1
        print "生成 %d 个礼包码" % count


if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        main(sys.argv[1])
    else:
        main(u'.')
