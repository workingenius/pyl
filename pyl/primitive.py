# -*- coding:utf8 -*-

""" Primitive Procedures -- 原始过程及其实现"""

from typing import List

from .base import ComputationalObject, Number, Boolean
from .evaluator import ProcedureBase, Parameter


class Primitive(object):
    @property
    def keyword(self):
        # type: () -> str
        raise NotImplementedError


class Plus(Primitive, ProcedureBase):
    keyword = '+'

    parameter = Parameter(['a', 'b'])

    def call(self, *nums: List[ComputationalObject]) -> ComputationalObject:
        return Number(sum([x.value for x in nums]))


class Minus(Primitive, ProcedureBase):
    keyword = '-'

    parameter = Parameter(['a', 'b'])

    def call(self, a, b):
        return Number(a.value - b.value)


class Multiply(Primitive, ProcedureBase):
    keyword = '*'

    parameter = Parameter(['a', 'b'])

    def call(self, a, b):
        return Number(a.value * b.value)


class Divide(Primitive, ProcedureBase):
    keyword = '/'

    parameter = Parameter(['a', 'b'])

    def call(self, a, b):
        return Number(a.value / b.value)


class Remainder(Primitive, ProcedureBase):
    keyword = 'remainder'

    parameter = Parameter(['a', 'b'])

    def call(self, a, b):
        return Number(a.value % b.value)


class Equal(Primitive, ProcedureBase):
    keyword = '='

    parameter = Parameter(['a', 'b'])

    def call(self, a, b):
        return Boolean(a.value == b.value)


class GreaterThan(Primitive, ProcedureBase):
    keyword = '>'

    parameter = Parameter(['a', 'b'])

    def call(self, a, b):
        return Boolean(a.value > b.value)


class LessThan(Primitive, ProcedureBase):
    keyword = '<'

    parameter = Parameter(['a', 'b'])

    def call(self, a, b):
        return Boolean(a.value < b.value)


class Car(Primitive, ProcedureBase):
    keyword = 'car'

    parameter = Parameter(['expr'])

    def call(self, expr):
        return expr.car


class Cdr(Primitive, ProcedureBase):
    keyword = 'cdr'

    parameter = Parameter(['expr'])

    def call(self, expr):
        return expr.cdr


primitives = [
    Plus(),
    Minus(),
    Multiply(),
    Divide(),
    Remainder(),
    Equal(),
    GreaterThan(),
    LessThan(),
    Car(),
    Cdr(),
]
