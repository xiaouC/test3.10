from yy.utils import DictObject

g_formulas = DictObject()

def register_formula(fn_or_name):
    'decorator'
    if callable(fn_or_name):
        g_formulas[fn_or_name.__name__] = fn_or_name
        return fn_or_name
    else:
        def decorator(func):
            g_formulas[fn_or_name] = func
            return func
        return decorator
