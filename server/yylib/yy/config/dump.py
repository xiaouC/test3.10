# coding: utf-8
import os
import csv
import json
import time
from cStringIO import StringIO
from datetime import datetime, date
from .fields import ValidationError


class DatetimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (datetime, date)):
            return int(time.mktime(obj.timetuple()))
        else:
            return json.JSONEncoder.default(self, obj)


def clean_header(header):
    'clean utf-8 bom header'
    return map(lambda s: s.replace('\xef\xbb\xbf', '')
                          .strip().decode('utf-8'), header)


def config_path(name, basepath):
    'return csv absolute path'
    return os.path.join(basepath, '%s.csv' % name)


def read_file(path):
    reader = csv.reader(open(path))
    header = reader.next()
    name, _ = os.path.splitext(os.path.basename(path))
    return name, clean_header(header), reader, path


def read_string(source):
    reader = csv.reader(StringIO(source))
    header = reader.next()
    return None, clean_header(header), reader, None


def load_csv(cls, name, source=None):
    try:
        if source is not None:
            prefix = u'文件%s，' % cls.__Meta__.table
            return cls.load_csv(*read_string(source))
        else:
            if not isinstance(cls.__Meta__.table, tuple):
                tables = [cls.__Meta__.table]
            else:
                tables = cls.__Meta__.table
            result = cls.get_container()
            for table in tables:
                prefix = u'文件%s，' % table
                data = cls.load_csv(*read_file(name))
                if isinstance(result, dict):
                    result.update(data)
                else:
                    result.extend(data)
            return result
    except ValidationError as e:
        raise ValidationError(prefix + e.message)


def dump(configs, path, **sources):
    alldata = {}
    # 加载csv
    for cls in configs:
        name = config_path(cls.__Meta__.table, path)
        source = sources.get(cls.__Meta__.table, None)
        alldata[cls.__name__] = load_csv(cls, name, source=source)
    # 校验csv数据
    for cls in configs:
        cls.post_validation(alldata)
    # 导出tuple {tblname: [[f,f,f,f], [f,f,f,f], ...] }
    result = {}
    for cls in configs:
        data = alldata[cls.__name__]
        result[cls.__name__] = l = []
        if cls.groupkey_field is not None:
            for its in data.values():
                items = its.values() if isinstance(its, dict) else its
                for item in items:
                    l.append(cls.to_tuple(item))
        else:
            for item in data.values() if isinstance(data, dict) else data:
                l.append(cls.to_tuple(item))
    # 导出
    return json.dumps(result, cls=DatetimeEncoder)
