# -*- coding:utf8 -*-
from typing import Optional

from pyl.structure import *
from .datatype import *
from .environment import Environment
from .helpers import list_to_pylist


def evaluate(expression: Expression, environment: Environment) -> ComputationalObject:
    evaluator = classify(expression)
    return evaluator.eval(expression, environment)


def evaluate_sequence(expression_lst: Expression, environment: Environment) -> ComputationalObject:
    co_lst = [evaluate(expr, environment) for expr in list_to_pylist(expression_lst)]
    if co_lst:
        return co_lst[-1]


def classify(expression: Expression) -> Optional['Evaluator']:
    """给表达式分类，决定用哪个 Structure 来解释

    没有找到分类，则返回 None
    """
    ess: List[Evaluator] = _evaluator_search_sequence

    for evaluator in ess:
        if evaluator.adapt(expression):
            return evaluator


class Evaluator(object):
    def adapt(self, expression: Expression) -> bool:
        """判断某 表达式是否属于此类型，适合用此类型的方法来解释"""
        raise NotImplementedError

    def eval(self, expression: Expression, environment: Environment) -> ComputationalObject:
        raise NotImplementedError


class ESelfEvaluating(Evaluator):
    """针对 解释为自己的表达式 的解释"""

    def adapt(self, expression):
        return isinstance(expression, (Number, String, Boolean))

    def eval(self, expression, environment):
        return expression


class EVariable(Evaluator):
    """针对 变量 的解释"""

    def adapt(self, expression):
        return isinstance(expression, Symbol)

    def eval(self, expression: Expression, environment: Environment) -> ComputationalObject:
        ret = environment.get(expression.value)
        return ret


class EQuoted(Evaluator):
    """针对 引用 的解释"""

    def adapt(self, expression: Expression) -> bool:
        return SQuoted.adapt(expression)

    def eval(self, expression: Expression, environment: Environment) -> ComputationalObject:
        return SQuoted(expression).quoted


class EAssignment(Evaluator):
    """针对 赋值 的解释"""

    def adapt(self, expression: Expression) -> bool:
        return SAssignment.adapt(expression)

    def eval(self, expression: Expression, environment: Environment) -> ComputationalObject:
        s = SAssignment(expression)
        name = s.variable_name
        value = evaluate(s.assignment_body, environment)
        environment.set(name.value, value)
        return Symbol('ok')


class EDefinition(Evaluator):
    """针对 define 的解释"""

    def adapt(self, expression: Expression) -> bool:
        return SDefinition.adapt(expression)

    def eval(self, expression: Expression, environment: Environment) -> ComputationalObject:
        d = SDefinition(expression)
        name = d.name.value
        proc = Procedure(
            parameter=d.parameter,
            body=d.body,
            environment=environment
        )
        environment.set(name, proc)
        return Symbol('ok')


class ESequence(Evaluator):
    def adapt(self, expression: Expression) -> bool:
        return SSequence.adapt(expression)

    def eval(self, expression: Expression, environment: Environment) -> ComputationalObject:
        return evaluate_sequence(SSequence(expression).sequence, environment)


class EIf(Evaluator):
    def adapt(self, expression: Expression) -> bool:
        return SIf.adapt(expression)

    def eval(self, expression: Expression, environment: Environment) -> ComputationalObject:
        i = SIf(expression)

        cond = evaluate(i.condition, environment)
        if is_true(cond):
            ret = evaluate(i.consequence, environment)
        else:
            ret = evaluate(i.alternative, environment)
        return ret


class ELambda(Evaluator):
    def adapt(self, expression: Expression) -> bool:
        return SLambda.adapt(expression)

    def eval(self, expression: Expression, environment: Environment) -> ComputationalObject:
        l = SLambda(expression)
        return Procedure(
            parameter=l.parameter,
            body=l.body,
            environment=environment
        )


class EAnd(Evaluator):
    def adapt(self, expression: Expression) -> bool:
        return SAnd.adapt(expression)

    def eval(self, expression: Expression, environment: Environment) -> ComputationalObject:
        for item in SAnd(expression).item_lst:
            if is_false(evaluate(item, environment)):
                return Boolean(False)
        return Boolean(True)


class EOr(Evaluator):
    def adapt(self, expression: Expression) -> bool:
        return SOr.adapt(expression)

    def eval(self, expression: Expression, environment: Environment) -> ComputationalObject:
        for item in SOr(expression).item_lst:
            if is_true(evaluate(item, environment)):
                return Boolean(True)
        return Boolean(False)


class ECond(Evaluator):
    def adapt(self, expression: Expression) -> bool:
        return SCond.adapt(expression)

    def _expand(self, branch_lst):
        """展开成 if 表达式"""
        ret = None

        if len(branch_lst) > 1:
            br_0 = branch_lst[0]
            br_rest = branch_lst[1:]

            ret = SIf(condition=br_0.test,
                      consequence=SSequence(sequence=br_0.then).expression,
                      alternative=self._expand(br_rest))

        elif len(branch_lst) == 1:
            br = branch_lst[0]

            if br.is_else:
                ret = SSequence(sequence=br.then).expression
            else:
                ret = SIf(condition=br.test,
                          consequence=SSequence(sequence=br.then).expression)

        return ret

    def eval(self, expression: Expression, environment: Environment) -> ComputationalObject:
        return evaluate(self._expand(SCond(expression).branch_lst), environment)


class EApplication(Evaluator):
    def adapt(self, expression: Expression) -> bool:
        return SApplication.adapt(expression)

    def eval(self, expression: Expression, environment: Environment) -> ComputationalObject:
        a = SApplication(expression)
        proc = evaluate(a.procedure_expression, environment)
        args = [evaluate(expr, environment) for expr in a.argument_lst]
        return proc.call(*args)


_evaluator_search_sequence = [
    ESelfEvaluating(),
    EVariable(),
    EQuoted(),
    EAssignment(),
    EDefinition(),
    ESequence(),
    EIf(),
    ECond(),
    EOr(),
    EAnd(),
    ELambda(),
    EApplication(),
]
