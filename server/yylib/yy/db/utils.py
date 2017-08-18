from yy.utils import DictObject

def dict_rows(ds):
    fields = [name for name,_ in ds.fields]
    return [DictObject(zip(fields, row)) for row in ds.rows]

def iter_dict_rows(ds):
    fields = [name for name, _ in ds.fields]
    return (dict(zip(fields, row)) for row in ds.rows)

def compress_hgetall(rs):
    result = []
    for i in range(0, len(rs), 2):
        result.append(rs[i:i+2])
    return dict(result)
