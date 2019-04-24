# -*- coding:utf8 -*-

u""" Primitive Procedures -- 原始过程及其实现"""

try:
    # noinspection PyUnresolvedReferences
    from typing import List, Optional, Union, Dict, Type, Callable
except ImportError:
    pass

from .evaluator import PrimitiveProcedure
from .base import ComputationalObject, Symbol, Number


class Plus(PrimitiveProcedure):
    keyword = Symbol('+')

    def call(self, *nums):  # type: (List[ComputationalObject]) -> ComputationalObject
        return Number(sum(map(lambda x: x.value, nums)))


class Minus(PrimitiveProcedure):
    keyword = Symbol('-')

    def call(self, a, b):
        return Number(a.value - b.value)


class Multiply(PrimitiveProcedure):
    keyword = Symbol('*')

    def call(self, a, b):
        return Number(a.value * b.value)


primitives = [
    Plus(),
    Minus(),
    Multiply(),
]
