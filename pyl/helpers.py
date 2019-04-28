# -*- coding:utf8 -*-
from .base import Pair, NIL


def pylist_to_list(py_lst):
    if len(py_lst) > 0:
        ret = Pair(
            py_lst[0],
            pylist_to_list(py_lst[1:])
        )
    else:
        ret = NIL
    return ret


def cons_list(*elements):
    return pylist_to_list(elements)


def list_to_pylist(lst):
    py_lst = []

    pair = lst
    while isinstance(pair, Pair):
        py_lst.append(pair.car)
        pair = pair.cdr

    return py_lst
