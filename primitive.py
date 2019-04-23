# -*- coding:utf8 -*-

try:
    # noinspection PyUnresolvedReferences
    from typing import List, Optional, Union, Dict, Type, Callable
except ImportError:
    pass

from pyl import PrimitiveProcedure, Symbol, Number, ComputationalObject


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
