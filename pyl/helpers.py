# -*- coding:utf8 -*-
from .base import Pair, NIL, Nil


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
    if not isinstance(pair, Nil):
        from .evaluator import EvaluatorSyntaxError
        raise EvaluatorSyntaxError('in fact a dotted list')

    return py_lst
