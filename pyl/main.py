# -*- coding:utf8 -*-

"""evaluator entrance

解释器入口
接受要解释的数据，而不是文本表示的代码

当作一个表达式解释，还是当作表达式序列解释，留给调用者决定
"""

__all__ = ['evaluate', 'evaluate_sequence']

from .environment import init_environment
from .analyze import evaluate as _evaluate, evaluate_sequence as _evaluate_sequence


def evaluate(expression):
    environment = init_environment()
    return _evaluate(expression, environment)


def evaluate_sequence(expression_lst):
    environment = init_environment()
    return _evaluate_sequence(expression_lst, environment)
