# -*- coding:utf8 -*-

"""基础数据结构"""

from typing import Union


class ComputationalObject(object):
    def __eq__(self, other):
        return self.__class__ == other.__class__ and self.__dict__ == other.__dict__


Expression = ComputationalObject


class Symbol(ComputationalObject):
    def __init__(self, value: str):
        self.value: str = value

    def __str__(self):
        return self.value


class Number(ComputationalObject):
    def __init__(self, value: int):
        self.value: int = value

    def __str__(self):
        return str(self.value)


class String(ComputationalObject):
    def __init__(self, value: str):
        self.value: str = value

    def __str__(self):
        return '"%s"' % self.value


class Boolean(ComputationalObject):
    def __init__(self, value: bool):
        self.value: bool = value

    def __str__(self):
        return '#f' if not self.value else '#t'


class Pair(ComputationalObject):
    def __init__(self, car: ComputationalObject, cdr: ComputationalObject):
        self.car: ComputationalObject = car
        self.cdr: ComputationalObject = cdr

    def format(self, closed=True):
        car = str(self.car)

        if isinstance(self.cdr, Pair):
            cdr = self.cdr.format(closed=False)
            ret = '{} {}'.format(car, cdr)

        elif isinstance(self.cdr, Nil):
            ret = car

        else:
            cdr = str(self.cdr)
            ret = '{} . {}'.format(car, cdr)

        if closed:
            ret = '({})'.format(ret)

        return ret

    def __str__(self):
        return self.format(closed=True)


class Nil(ComputationalObject):
    def __str__(self):
        return 'nil'


NIL = Nil()

LispList = Union[Pair, Nil]


def is_true(v):
    assert isinstance(v, ComputationalObject)
    return not is_false(v)


def is_false(v):
    assert isinstance(v, ComputationalObject)
    return v == Boolean(False)
