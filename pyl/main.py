# -*- coding:utf8 -*-

u"""evaluator entrance"""

__all__ = ['evaluate', 'evaluate_sequence']

# TODO: entrance accept code as text and parse it

from .environment import init_environment
from .evaluator import evaluate as _evaluate, evaluate_sequence as _evaluate_sequence


def evaluate(expression):
    environment = init_environment()
    return _evaluate(expression, environment)


def evaluate_sequence(expression_lst):
    environment = init_environment()
    return _evaluate_sequence(expression_lst, environment)
