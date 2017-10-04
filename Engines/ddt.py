#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from ddt import *


# Patch ddt module
# Digits of the largest index of cases for list/tuple, or default = 5 for generator
INDEX_LEN = len(str(len(DATA_ATTR))) if isinstance(DATA_ATTR, (list, tuple)) else 5

def mk_test_name(name, value, index=0):
    # Add zeros before index
    index = str(index + 1)
    if len(index) < INDEX_LEN:
        index = '0' * (INDEX_LEN - len(index)) + index
    if not is_trivial(value):
        return "{0}_{1}".format(name, index)
    try:
        value = str(value)
    except UnicodeEncodeError:
        # fallback for python2
        value = value.encode('ascii', 'backslashreplace')
    test_name = "{0}_{1}_{2}".format(name, index, value)
    return re.sub(r'\W|^(?=\d)', '_', test_name)


def ddt(cls):
    for name, func in list(cls.__dict__.items()):
        if hasattr(func, DATA_ATTR):
            for i, v in enumerate(getattr(func, DATA_ATTR)):
                test_name = mk_test_name(name, getattr(v, "__name__", v), i)
                if hasattr(func, UNPACK_ATTR):
                    if isinstance(v, tuple) or isinstance(v, list):
                        add_test(cls, test_name, func, *v)
                    else:
                        # unpack dictionary
                        add_test(cls, test_name, func, **v)
                else:
                    add_test(cls, test_name, func, v)
            delattr(cls, name)
        elif hasattr(func, FILE_ATTR):
            file_attr = getattr(func, FILE_ATTR)
            process_file_data(cls, name, func, file_attr)
            delattr(cls, name)
    return cls
