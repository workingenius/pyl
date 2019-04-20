# -*- coding: utf-8 -*-


try:
    # noinspection PyUnresolvedReferences
    from typing import List
except ImportError:
    pass


# list data structure


class Expression(object):
    def __eq__(self, other):
        return self.__class__ == other.__class__ and self.__dict__ == other.__dict__


class SymbolExpr(Expression):
    def __init__(self, value):
        # type: (str) -> None
        self.value = value  # type: str


class NumberExpr(Expression):
    def __init__(self, value):
        # type: (int) -> None
        self.value = value  # type: int


class StringExpr(Expression):
    def __init__(self, value):
        # type: (str) -> None
        self.value = value  # type: str


class FalseExpr(Expression):
    pass


class ListExpr(Expression):
    def __init__(self, sub_expr_lst):
        # type: (List[Expression]) -> None
        self.sub_expr_lst = sub_expr_lst  # type: List[Expression]


# evaluator


class Environment(object):
    pass


def evaluate(expression, environment=None):
    # type: (Expression, Environment) -> Expression
    raise NotImplementedError
