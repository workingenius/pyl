# -*- coding:utf8 -*-
from .base import ComputationalObject, Symbol, Expression, Number, String, Boolean, Pair, is_true, is_false, NIL
from .environment import Environment
from .helpers import cons_list, list_to_pylist, pylist_to_list

try:
    # noinspection PyUnresolvedReferences
    from typing import List, Optional, Union, Dict, Type, Callable
except ImportError:
    pass


class Parameter(object):
    def __init__(self, names):
        self.names = names  # type: List[str]


class ProcedureBase(ComputationalObject):
    @property
    def parameter(self):
        # type: () -> Parameter
        """参数表"""
        raise NotImplementedError

    def call(self, *arguments):
        # type: (*list) -> ComputationalObject
        raise NotImplementedError

    def apply(self, *args):
        return self.call(*args)


class Procedure(ProcedureBase):
    def __init__(self, parameter, body, environment):
        # type: (Parameter, Expression, Environment) -> None

        assert isinstance(body, Expression)
        assert isinstance(environment, Environment)

        self._parameter = parameter  # type: Parameter
        self.body = body  # type: Expression
        self.environment = environment  # type: Environment

    @property
    def parameter(self):  # type: () -> Parameter
        return self._parameter

    def call(self, *arguments):
        # type: (List[ComputationalObject]) -> ComputationalObject

        env = self.environment.extend()
        for param, arg in zip(self.parameter.names, arguments):
            env.set(param, arg)

        return evaluate_sequence(self.body, env)


def evaluate(expression, environment):
    # type: (Expression, Environment) -> ComputationalObject
    evaluator_class = classify(expression)
    return evaluator_class(expression).eval(environment)


def evaluate_sequence(expression_lst, environment):
    # type: (Expression, Environment) -> ComputationalObject
    co_lst = [evaluate(expr, environment) for expr in list_to_pylist(expression_lst)]
    if co_lst:
        return co_lst[-1]


def classify(expression):
    # type: (Expression) -> Optional[type]
    """给表达式分类，决定用哪个 Structure 来解释

    没有找到分类，则返回 None
    """
    ess = _evaluator_search_sequence  # type: List[Type[Evaluator]]

    for evaluator_class in ess:
        if evaluator_class.adapt(expression):
            return evaluator_class


class Structure(object):
    """
    `结构` 可以按照语法把表达式分解成各关键部分，和根据语法把各关键部分组合成表达式

    实现结构与语法的解耦
    """

    def dismantle(self):  # type: () -> None
        """把完整表达式分解成关键部分"""
        raise NotImplementedError

    def construct(self):  # type: () -> Expression
        """用关键部分拼成表达式"""
        raise NotImplementedError

    def __init__(self):
        if getattr(self, 'expression', None):
            self.dismantle()
        else:
            self.expression = self.construct()


class Evaluator(object):
    @classmethod
    def adapt(cls, expression):  # type: (Expression) -> bool
        """判断某 表达式是否属于此类型，适合用此类型的方法来解释"""
        raise NotImplementedError

    def eval(self, environment):
        # type: (Environment) -> ComputationalObject
        raise NotImplementedError


class NoPartsMixin(object):
    def dismantle(self):
        pass

    def construct(self):
        raise Exception('should not get here')


class ESelfEvaluating(NoPartsMixin, Structure, Evaluator):
    """针对 解释为自己的表达式 的解释"""

    @classmethod
    def adapt(cls, expression):
        return isinstance(expression, (Number, String, Boolean))

    def __init__(self, expression):
        self.expression = expression
        super(self.__class__, self).__init__()

    def eval(self, environment):
        return self.expression


class EVariable(NoPartsMixin, Structure, Evaluator):
    """针对 变量 的解释"""

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
    """特殊形式的工具方法"""

    @staticmethod
    def first_symbol(expression):  # type: (Expression) -> Optional[Expression]
        """如果列表有多个元素，且第一个是 symbol，则返回之，否则返回 None

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
            ret = cls.index(lst.cdr, index - 1)

        return ret

    @classmethod
    def adapt(cls, expression):  # type: (Expression) -> bool
        return cls.first_symbol(expression) == Symbol(cls.keyword)


class EQuoted(ESpecialFormMixin, Structure, Evaluator):
    """针对 引用 的解释"""
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
        return Pair(Symbol(self.keyword), Pair(self.quoted, NIL))

    def eval(self, environment):  # type: (Environment) -> ComputationalObject
        return self.quoted


class EAssignment(ESpecialFormMixin, Structure, Evaluator):
    """针对 赋值 的解释"""
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
        return symbol_as_var_name.value

    def _assignment_body(self):  # type: () -> Expression
        body_expr = self.index(self.expression, 2)
        return body_expr

    def construct(self):  # type: () -> Expression
        return Pair(Symbol(self.keyword), Pair(self.variable_name, self.assignment_body))

    def eval(self, environment):  # type: (Environment) -> ComputationalObject
        name = self.variable_name
        value = evaluate(self.assignment_body, environment)
        # TODO: bug
        environment.set(name, value)
        return Symbol('ok')


class EDefinition(ESpecialFormMixin, Structure, Evaluator):
    """针对 define 的解释"""
    keyword = 'define'

    @classmethod
    def adapt(cls, expression):  # type: (Expression) -> bool
        return cls.first_symbol(expression) == Symbol(cls.keyword) \
               and isinstance(expression, Pair) \
               and isinstance(cls.index(expression, 1), Pair)

    def __init__(self, expression=None, name=None, parameter=None, body=None):
        self.expression = expression  # type: Expression
        self.name = name  # type: Symbol
        self.parameter = parameter  # type: Parameter
        self.body = body  # type: Pair
        super(self.__class__, self).__init__()

    def dismantle(self):  # type: () -> None
        self.name = self.expression.cdr.car.car
        self.parameter = EParameter(expression=self.expression.cdr.car.cdr).parameter
        self.body = self.expression.cdr.cdr

    def construct(self):  # type: () -> Expression
        if not isinstance(self.parameter, Parameter):
            raise TypeError('parameter of definition should be a Parameter')

        return cons_list(Symbol(self.keyword),
                         Pair(self.name, EParameter(parameter=self.parameter).expression),
                         self.body)

    def eval(self, environment):  # type: (Environment) -> ComputationalObject
        name = self.name.value
        proc = Procedure(
            parameter=self.parameter,
            body=self.body,
            environment=environment
        )
        environment.set(name, proc)
        return Symbol('ok')


class ESequence(ESpecialFormMixin, Structure, Evaluator):
    keyword = 'begin'

    def __init__(self, expression=None, sequence=None):
        self.expression = expression  # type: Pair
        self.sequence = sequence  # type: Expression
        super(self.__class__, self).__init__()

    def dismantle(self):  # type: () -> None
        self.sequence = self.expression.cdr

    def construct(self):  # type: () -> Expression
        return Pair(Symbol(self.keyword), self.sequence)

    @classmethod
    def adapt(cls, expression):  # type: (Expression) -> bool
        return cls.first_symbol(expression) == Symbol(cls.keyword)

    def eval(self, environment):  # type: (Environment) -> ComputationalObject
        return evaluate_sequence(self.sequence, environment)


class EIf(ESpecialFormMixin, Structure, Evaluator):
    keyword = 'if'

    def __init__(self, expression=None, condition=None, consequence=None, alternative=None):
        self.expression = expression  # type: Expression
        self.condition = condition  # type: Expression
        self.consequence = consequence  # type: Expression
        self.alternative = alternative  # type: Expression
        super(self.__class__, self).__init__()

    def dismantle(self):  # type: () -> None
        self.condition = self.expression.cdr.car
        self.consequence = self.expression.cdr.cdr.car
        self.alternative = self.expression.cdr.cdr.cdr.car

    def construct(self):  # type: () -> Expression
        return cons_list(self.condition, self.consequence, self.alternative)

    @classmethod
    def adapt(cls, expression):  # type: (Expression) -> bool
        return cls.first_symbol(expression) == Symbol(cls.keyword)

    def eval(self, environment):  # type: (Environment) -> ComputationalObject
        cond = evaluate(self.condition, environment)
        if is_true(cond):
            ret = evaluate(self.consequence, environment)
        else:
            ret = evaluate(self.alternative, environment)
        return ret


class ELambda(ESpecialFormMixin, Structure, Evaluator):
    keyword = 'lambda'

    def __init__(self, expression=None, parameter=None, body=None):
        self.expression = expression  # type: Expression
        self.parameter = parameter  # type: Parameter
        self.body = body  # type: Expression
        super(self.__class__, self).__init__()

    def dismantle(self):  # type: () -> None
        self.parameter = EParameter(self.expression.cdr.car).parameter
        self.body = self.expression.cdr.cdr

    def construct(self):  # type: () -> Expression
        return cons_list(Symbol(self.keyword), pylist_to_list(self.parameter), pylist_to_list(self.body))

    def eval(self, environment):  # type: (Environment) -> ComputationalObject
        return Procedure(parameter=self.parameter, body=self.body, environment=environment)


class EAnd(ESpecialFormMixin, Structure, Evaluator):
    keyword = 'and'

    def __init__(self, expression=None, item_lst=None):
        self.expression = expression  # type: Expression
        self.item_lst = item_lst  # type: List[Expression]
        super(self.__class__, self).__init__()

    def dismantle(self):  # type: () -> None
        self.item_lst = list_to_pylist(self.expression.cdr)

    def construct(self):  # type: () -> Expression
        return pylist_to_list(self.item_lst)

    def eval(self, environment):  # type: (Environment) -> ComputationalObject
        for item in self.item_lst:
            if is_false(evaluate(item, environment)):
                return Boolean(False)
        return Boolean(True)


class EOr(ESpecialFormMixin, Structure, Evaluator):
    keyword = 'or'

    def __init__(self, expression=None, item_lst=None):
        self.expression = expression  # type: Expression
        self.item_lst = item_lst  # type: List[Expression]
        super(self.__class__, self).__init__()

    def dismantle(self):  # type: () -> None
        self.item_lst = list_to_pylist(self.expression.cdr)

    def construct(self):  # type: () -> Expression
        return pylist_to_list(self.item_lst)

    def eval(self, environment):  # type: (Environment) -> ComputationalObject
        for item in self.item_lst:
            if is_true(evaluate(item, environment)):
                return Boolean(True)
        return Boolean(False)


class SCondBranch(Structure):
    def __init__(self, expression=None, is_else=None, test=None, then=None):
        self.expression = expression  # type: Expression
        self.is_else = is_else  # type: bool
        self.test = test  # type: Expression
        self.then = then  # type: Expression
        super(self.__class__, self).__init__()

    def dismantle(self):  # type: () -> None
        self.is_else = self.expression.car == Symbol('else')
        self.test = self.expression.car
        self.then = self.expression.cdr

    def construct(self):  # type: () -> Expression
        return Pair(self.test, self.then)


class ECond(ESpecialFormMixin, Structure, Evaluator):
    keyword = 'cond'

    def __init__(self, expression=None, branch_lst=None):
        self.expression = expression  # type: Expression
        self.branch_lst = branch_lst  # type: List[SCondBranch]
        super(self.__class__, self).__init__()

    def dismantle(self):  # type: () -> None
        self.branch_lst = list(map(SCondBranch, list_to_pylist(self.expression.cdr)))

    def construct(self):  # type: () -> Expression
        return Pair(Symbol(self.keyword), pylist_to_list([c.expression for c in self.branch_lst]))

    def _expand(self, branch_lst):
        """展开成 if 表达式"""
        ret = None

        if len(branch_lst) > 1:
            br_0 = branch_lst[0]
            br_rest = branch_lst[1:]

            ret = EIf(condition=br_0.test,
                      consequence=ESequence(sequence=br_0.then).expression,
                      alternative=self._expand(br_rest))

        elif len(branch_lst) == 1:
            br = branch_lst[0]

            if br.is_else:
                ret = ESequence(sequence=br.then).expression
            else:
                ret = EIf(condition=br.test,
                          consequence=ESequence(sequence=br.then).expression)

        return ret

    def eval(self, environment):  # type: (Environment) -> ComputationalObject
        expanded = self._expand(self.branch_lst)
        if expanded:
            return expanded.eval(environment)


class EApplication(Structure, Evaluator):
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
        args = [evaluate(expr, environment) for expr in self.argument_lst]
        return proc.call(*args)


_evaluator_search_sequence = [
    ESelfEvaluating,
    EVariable,
    EQuoted,
    EAssignment,
    EDefinition,
    ESequence,
    EIf,
    ECond,
    EOr,
    EAnd,
    ELambda,
    EApplication,
]


class EParameter(Structure):
    def __init__(self, expression=None, parameter=None):
        self.expression = expression  # type: Expression
        self.parameter = parameter  # type: Parameter
        super(self.__class__, self).__init__()

    def dismantle(self):  # type: () -> None
        self.parameter = Parameter(names=[expr.value for expr in list_to_pylist(self.expression)])

    def construct(self):  # type: () -> Expression
        return pylist_to_list(list(map(Symbol, self.parameter.names)))
