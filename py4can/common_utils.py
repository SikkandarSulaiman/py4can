import os
import inspect
from pathlib import Path
from functools import wraps
from functools import partial


class KeyFrozenDict(dict):
    """ Creates a dictionary with initial set of keys, after which
    new keys cannot be added neither initial keys can be removed"""
    _setitem_callback = None

    def __init__(self, *args, **kwargs):
        try:
            __class__._setitem_callback = kwargs['setitem_callback']
            kwargs.pop('setitem_callback')
        except KeyError:
            pass
        self.update(*args, **kwargs)

    @property
    def setitem_callback(self):
        return __class__._setitem_callback

    @setitem_callback.setter
    def setitem_callback(self, new_callback):
        __class__._setitem_callback = new_callback

    def __setitem__(self, key, value):
        if key not in self.keys():
            raise KeyError
        super().__setitem__(key, value)
        if __class__._setitem_callback:
            __class__._setitem_callback(*(key, value))


class IndexFrozenList(list):
    """ Creates a list of arbitrary length after which no item can
    be removed or added i.e. no change in length"""
    _setitem_callback = None

    def __init__(self, proto=None, setitem_callback=None):
        super().__init__()
        if type(proto) is int:
            proto = [0 for _ in range(proto)]
        super().extend(proto)
        if setitem_callback: __class__.setitem_callback = setitem_callback
        self._fixed_len = super()

    @property
    def setitem_callback(self):
        return __class__._setitem_callback

    @setitem_callback.setter
    def setitem_callback(self, new_callback):
        __class__._setitem_callback = new_callback

    def append(self, value): pass

    def extend(self, extn): pass

    def insert(self, pos, value): pass

    def pop(self, index): pass

    def remove(self, value): pass

    def __setitem__(self, index, value):
        super().__setitem__(index, value)
        if __class__._setitem_callback:
            __class__._setitem_callback(*(index, value))


def _path_safe(func, exec_dir):
    cwd = os.getcwd()
    caller_file = inspect.stack()[1].filename
    caller_file = str(Path(caller_file))
    caller_path = caller_file.rsplit(os.sep, maxsplit=1)[0]
    exec_dir = Path(caller_path) / Path(exec_dir) if exec_dir else Path(caller_path)

    @wraps(func)
    def wrapper(*args, **kwargs):
        os.chdir(exec_dir)
        result = func(*args, **kwargs)
        os.chdir(cwd)
        return result
    return wrapper


def path_safe(exec_dir=None):
    return partial(_path_safe, exec_dir)


def exec_in_path(func, path, *args, **kwargs):
    return path_safe(func)(path)(*args, **kwargs)
