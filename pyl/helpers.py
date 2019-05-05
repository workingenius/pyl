# -*- coding:utf8 -*-
from typing import Optional

from pyl.datatype import Expression, Symbol
from .datatype import Pair, NIL


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


def first_symbol(expression: Expression) -> Optional[Symbol]:
    """如果列表有多个元素，且第一个是 symbol，则返回之，否则返回 None

    列表的首个元素的 symbol 值，经常用作判定特殊形式的标识
    """
    if not isinstance(expression, Pair):
        return None

    e0 = expression.car
    if not isinstance(e0, Symbol):
        return None

    return e0


def by_index(lst: Expression, index: int) -> Optional[Expression]:
    """获取 lst 里的第 index 个元素，如果不存在则返回 None"""
    ret = None

    if not isinstance(index, int) or index < 0:
        raise ValueError

    elif not isinstance(lst, Pair):
        ret = None

    elif index == 0:
        pair = lst
        ret = pair.car

    elif index > 0:
        # noinspection PyTypeChecker
        ret = by_index(lst.cdr, index - 1)

    return ret
