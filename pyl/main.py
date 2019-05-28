# -*- coding:utf8 -*-

"""evaluator entrance

解释器入口
接受要解释的数据，而不是文本表示的代码

当作一个表达式解释，还是当作表达式序列解释，留给调用者决定
"""
from pyl.lazy import Thunk

__all__ = ['Evaluator']

from .environment import init_environment


class Evaluator(object):
    def __init__(self, bool_analyze):
        self.bool_analyze = bool(bool_analyze)

        if self.bool_analyze:
            from .analyze import evaluate, evaluate_sequence
        else:
            from .evaluator import evaluate, evaluate_sequence

        self._eval = evaluate
        self._eval_seq = evaluate_sequence
        self.env = init_environment()

    def eval(self, expression):
        return Thunk.force(self._eval(expression, self.env))

    def eval_seq(self, expression):
        return Thunk.force(self._eval_seq(expression, self.env))
