# -*- coding:utf8 -*-
from .base import ComputationalObject, Symbol, Expression, Number, String, Boolean, Pair
from .environment import Environment
from .helpers import cons_list, list_to_pylist, pylist_to_list

try:
    # noinspection PyUnresolvedReferences
    from typing import List, Optional, Union, Dict, Type, Callable
except ImportError:
    pass


class Procedure(ComputationalObject):
    def __init__(self, parameter, body, environment):
        # type: (List[Symbol], Expression, Environment) -> None

        for i, param in enumerate(parameter):
            assert isinstance(param, Symbol)

        assert isinstance(body, Expression)
        assert isinstance(environment, Environment)

        self.parameter = list(parameter)  # type: List[Symbol]
        self.body = body  # type: Expression
        self.environment = environment  # type: Environment

    def call(self, *arguments):
        # type: (List[ComputationalObject]) -> ComputationalObject

        env = self.environment.extend()
        for param, arg in zip(self.parameter, arguments):
            env.set(param.value, arg)

        return evaluate(self.body, env)


class PrimitiveProcedure(ComputationalObject):
    def __init__(self, py_procedure=None):
        self.py_procedure = py_procedure  # type: Optional[Callable]

    def call(self, *arguments):
        # type: (List[ComputationalObject]) -> ComputationalObject
        return self.py_procedure(*arguments)


def evaluate(expression, environment):
    # type: (Expression, Environment) -> ComputationalObject
    evaluator_class = classify(expression)
    return evaluator_class(expression).eval(environment)


def evaluate_sequence(expression_lst, environment):
    co_lst = map(lambda expr: evaluate(expr, environment), expression_lst)
    if co_lst:
        return co_lst[-1]


def classify(expression):
    # type: (Expression) -> Optional[type]
    u"""给表达式分类，决定用哪个 ExpressionType 来解释

    没有找到分类，则返回 None
    """
    ess = _evaluator_search_sequence  # type: List[Type[Evaluator]]

    for evaluator_class in ess:
        if evaluator_class.adapt(expression):
            return evaluator_class


class ExpressionType(object):
    def dismantle(self):  # type: () -> None
        u"""把完整表达式分解成关键部分"""
        raise NotImplementedError

    def construct(self):  # type: () -> Expression
        u"""用关键部分拼成表达式"""
        raise NotImplementedError

    def __init__(self):
        if getattr(self, 'expression', None):
            self.dismantle()
        else:
            self.expression = self.construct()


class Evaluator(object):
    @classmethod
    def adapt(cls, expression):  # type: (Expression) -> bool
        u"""判断某 表达式是否属于此类型，适合用此类型的方法来解释"""
        raise NotImplementedError

    def eval(self, environment):
        # type: (Environment) -> ComputationalObject
        raise NotImplementedError


class NoPartsMixin(object):
    def dismantle(self):
        pass

    def construct(self):
        raise Exception('should not get here')


class ESelfEvaluating(NoPartsMixin, ExpressionType, Evaluator):
    u"""针对 解释为自己的表达式 的解释"""

    @classmethod
    def adapt(cls, expression):
        return isinstance(expression, (Number, String, Boolean))

    def __init__(self, expression):
        self.expression = expression
        super(self.__class__, self).__init__()

    def eval(self, environment):
        return self.expression


class EVariable(NoPartsMixin, ExpressionType, Evaluator):
    u"""针对 变量 的解释"""

    @classmethod
    def adapt(cls, expression):
        return isinstance(expression, Symbol)

    def __init__(self, expression):
        self.expression = expression  # type: Symbol
        super(self.__class__, self).__init__()

    def eval(self, environment):
        ret = environment.get(self.expression.value)
        return ret


class ESpecialFormMixin(object):
    u"""特殊形式的工具方法"""

    @staticmethod
    def first_symbol(expression):  # type: (Expression) -> Optional[Expression]
        u"""如果列表有多个元素，且第一个是 symbol，则返回之，否则返回 None

        列表的首个元素的 symbol 值，经常用作判定特殊形式的标识
        """
        if not isinstance(expression, Pair):
            return None

        e0 = expression.car
        if not isinstance(e0, Symbol):
            return None

        return e0

    @classmethod
    def index(cls, lst, index):  # type: (Pair, int) -> Optional[Expression]
        u"""获取 lst 里的第 index 个元素，如果不存在则返回 None"""
        ret = None

        if not isinstance(index, int) or index < 0:
            raise ValueError

        elif not isinstance(lst, Pair):
            ret = None

        elif index == 0:
            pair = lst
            ret = pair.car

        elif index > 1:
            # noinspection PyTypeChecker
            ret = cls.index(lst.cdr, index - 1)

        return ret


class EQuoted(ESpecialFormMixin, ExpressionType, Evaluator):
    u"""针对 引用 的解释"""
    keyword = 'quote'

    @classmethod
    def adapt(cls, expression):  # type: (Expression) -> bool
        return cls.first_symbol(expression) == Symbol(cls.keyword)

    def __init__(self, expression=None, quoted=None):
        self.expression = expression  # type: Pair
        self.quoted = quoted  # type: Expression
        super(self.__class__, self).__init__()

    def dismantle(self):  # type: () -> None
        self.quoted = self.expression.cdr.car

    def construct(self):  # type: () -> Expression
        return Pair(Symbol(self.keyword), self.quoted)

    def eval(self, environment):  # type: (Environment) -> ComputationalObject
        return self.quoted


class EAssignment(ESpecialFormMixin, ExpressionType, Evaluator):
    u"""针对 赋值 的解释"""
    keyword = 'set!'

    @classmethod
    def adapt(cls, expr):  # type: (Expression) -> bool
        return cls.first_symbol(expr) == Symbol(cls.keyword)

    def __init__(self, expression=None, variable_name=None, assignment_body=None):
        self.expression = expression  # type: Pair
        self.variable_name = variable_name  # type: Symbol
        self.assignment_body = assignment_body  # type: Pair
        super(self.__class__, self).__init__()

    def dismantle(self):  # type: () -> None
        self.variable_name = self._variable_name()
        self.assignment_body = self._assignment_body()

    def _variable_name(self):  # type: () -> str
        symbol_as_var_name = self.index(self.expression, 1)
        self.verify_variable_name(symbol_as_var_name)
        return symbol_as_var_name.value

    def _assignment_body(self):  # type: () -> Expression
        body_expr = self.index(self.expression, 2)
        return body_expr

    def construct(self):  # type: () -> Expression
        self.verify_assignment_body(self.assignment_body)
        return Pair(Symbol(self.keyword), Pair(self.variable_name, self.assignment_body))

    def eval(self, environment):  # type: (Environment) -> ComputationalObject
        name = self.variable_name
        value = evaluate(self.assignment_body, environment)
        environment.set(name, value)
        return Symbol('ok')


class EDefinition(ESpecialFormMixin, ExpressionType, Evaluator):
    u"""针对 define 的解释"""
    keyword = 'define'

    @classmethod
    def adapt(cls, expression):  # type: (Expression) -> bool
        return cls.first_symbol(expression) == Symbol(cls.keyword) \
               and isinstance(expression, Pair) \
               and isinstance(cls.index(expression, 1), Pair)

    def __init__(self, expression=None, name=None, parameter=None, body=None):
        self.expression = expression  # type: Expression
        self.name = name  # type: Symbol
        self.parameter = parameter  # type: EParameter
        self.body = body  # type: Pair
        super(self.__class__, self).__init__()

    def dismantle(self):  # type: () -> None
        self.name = self._procedure_name(self.expression)
        self.parameter = self._parameter(self.expression)
        self.body = self._body(self.expression)

    def construct(self):  # type: () -> Expression
        if not isinstance(self.parameter, EParameter):
            raise TypeError('parameter of definition should be a EParameter')

        return cons_list(Symbol(self.keyword),
                         Pair(self.name, self.parameter.expression),
                         self.body)

    def eval(self, environment):  # type: (Environment) -> ComputationalObject
        name = self.name.value
        proc = Procedure(
            parameter=self.parameter.symbol_lst,
            body=self.body,
            environment=environment
        )
        environment.set(name, proc)
        return Symbol('ok')


class ESequence(ESpecialFormMixin, ExpressionType, Evaluator):
    keyword = 'begin'

    def __init__(self, expression=None, sequence=None):
        self.expression = expression  # type: Pair
        self.sequence = sequence  # type: List[Expression]
        super(self.__class__, self).__init__()

    def dismantle(self):  # type: () -> None
        seq = self.expression.cdr
        self.sequence = list_to_pylist(seq)

    def construct(self):  # type: () -> Expression
        return Pair(Symbol(self.keyword), pylist_to_list(self.sequence))

    @classmethod
    def adapt(cls, expression):  # type: (Expression) -> bool
        return cls.first_symbol(expression) == Symbol(cls.keyword)

    def eval(self, environment):  # type: (Environment) -> ComputationalObject
        return evaluate_sequence(self.sequence, environment)


class EApplication(ExpressionType, Evaluator):
    def __init__(self, expression=None, procedure_expression=None, argument_lst=None):
        self.expression = expression  # type: Pair
        self.procedure_expression = procedure_expression  # type: Expression
        self.argument_lst = argument_lst  # type: List[Expression]
        super(self.__class__, self).__init__()

    def dismantle(self):  # type: () -> None
        self.procedure_expression = self.expression.car
        self.argument_lst = list_to_pylist(self.expression.cdr)

    def construct(self):  # type: () -> Expression
        return Pair(self.procedure_expression, pylist_to_list(self.argument_lst))

    @classmethod
    def adapt(cls, expression):  # type: (Expression) -> bool
        return isinstance(expression, Pair)

    def eval(self, environment):  # type: (Environment) -> ComputationalObject
        proc = evaluate(self.procedure_expression, environment)
        args = map(lambda expr: evaluate(expr, environment), self.argument_lst)
        return proc.call(*args)


_evaluator_search_sequence = [
    ESelfEvaluating,
    EVariable,
    EQuoted,
    EAssignment,
    EDefinition,
    ESequence,
    EApplication,
]


class EParameter(ExpressionType):
    def __init__(self, expression=None, symbol_lst=None):
        self.expression = expression  # type: Expression
        self.symbol_lst = symbol_lst  # type: List[Symbol]
        super(self.__class__, self).__init__()

    def dismantle(self):  # type: () -> None
        param_lst = list_to_pylist(self.expression)
        self.symbol_lst = param_lst

    def construct(self):  # type: () -> Expression
        return pylist_to_list(self.symbol_lst)