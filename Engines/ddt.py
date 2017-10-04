#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from ddt import *


# Patch ddt module
def ddt(cls):
    for name, func in list(cls.__dict__.items()):
        if hasattr(func, DATA_ATTR):
            for i, v in enumerate(getattr(func, DATA_ATTR)):
                # fix the order of test cases
                fix_name = name + '0' if i < 9 else name
                test_name = mk_test_name(fix_name, getattr(v, "__name__", v), i)
                # test_name = mk_test_name(name, getattr(v, "__name__", v), i)
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
