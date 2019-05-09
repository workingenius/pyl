from typing import Type, List

from pyl.datatype import ComputationalObject, Expression, Number, String, Boolean, Symbol, ProcedureBase, Parameter, \
    is_true, is_false, NIL
from pyl.environment import Environment
from pyl.helpers import list_to_pylist
from pyl.structure import SQuoted, SAssignment, SDefinition, SSequence, SIf, SLambda, SAnd, SOr, SCond, SApplication, \
    SLet


def evaluate(expression: Expression, environment: Environment) -> ComputationalObject:
    return analyze(expression).eval(environment)


def evaluate_sequence(expression_lst: Expression, environment: Environment) -> ComputationalObject:
    # import pdb; pdb.set_trace()
    return analyze_sequence(expression_lst).eval(environment)


def analyze(expression: Expression) -> 'Analyzer':
    analyzer_class = classify(expression)
    if not analyzer_class:
        raise
    return analyzer_class(expression)


def analyze_sequence(expression_lst: Expression) -> 'Analyzer':
    return analyze(SSequence(sequence=expression_lst).expression)


def classify(expression: Expression) -> Type['Analyzer']:
    ess = analyzer_class_lst

    for ac in ess:
        if ac.adapt(expression):
            return ac


class Analyzer(object):
    @classmethod
    def adapt(cls, expression: Expression) -> bool:
        raise NotImplementedError

    def eval(self, environment: Environment) -> ComputationalObject:
        raise NotImplementedError


class Procedure(ProcedureBase):
    def __init__(self, parameter: Parameter, body: Analyzer, environment: Environment):
        assert isinstance(body, Analyzer)
        assert isinstance(environment, Environment)

        self._parameter: Parameter = parameter
        self.code_lst = list_to_pylist(body)
        self.body: Analyzer = body
        self.environment: Environment = environment

    @property
    def parameter(self) -> Parameter:
        return self._parameter

    def call(self, *arguments: List[ComputationalObject]) -> ComputationalObject:
        env = self.environment.extend()
        for param, arg in zip(self.parameter.names, arguments):
            env.set(param, arg)
        return self.body.eval(env)


class ASelfEvaluating(Analyzer):
    @classmethod
    def adapt(cls, expression):
        return isinstance(expression, (Number, String, Boolean))

    def __init__(self, expression: Expression):
        self.value = expression

    def eval(self, environment):
        return self.value


class AVariable(Analyzer):
    @classmethod
    def adapt(cls, expression):
        return isinstance(expression, Symbol)

    def __init__(self, expression):
        self.name = expression.value

    def eval(self, environment: Environment) -> ComputationalObject:
        ret = environment.get(self.name)
        return ret


class AQuoted(Analyzer):
    @classmethod
    def adapt(cls, expression: Expression) -> bool:
        return SQuoted.adapt(expression)

    def __init__(self, expression):
        self.data = SQuoted(expression).quoted

    def eval(self, environment: Environment) -> ComputationalObject:
        return self.data


class AAssignment(Analyzer):
    @classmethod
    def adapt(cls, expression: Expression) -> bool:
        return SAssignment.adapt(expression)

    def __init__(self, expression):
        s = SAssignment(expression)
        self.name = s.variable_name.value
        self.value_code = analyze(s.assignment_body)

    def eval(self, environment: Environment) -> ComputationalObject:
        environment.set(self.name, self.value_code.eval(environment))
        return Symbol('ok')


class ADefinition(Analyzer):
    @classmethod
    def adapt(cls, expression: Expression) -> bool:
        return SDefinition.adapt(expression)

    def __init__(self, expression):
        d = SDefinition(expression)
        self.name = d.name.value
        self.parameter = d.parameter
        self.proc_code = analyze_sequence(d.body)

    def eval(self, environment: Environment) -> ComputationalObject:
        proc = Procedure(
            parameter=self.parameter,
            body=self.proc_code,
            environment=environment
        )
        environment.set(self.name, proc)
        return Symbol('ok')


class ASequence(Analyzer):
    @classmethod
    def adapt(cls, expression: Expression) -> bool:
        return SSequence.adapt(expression)

    def __init__(self, expression):
        seq = list_to_pylist(SSequence(expression).sequence)
        self.sequence = _mp(analyze, seq)

    def eval(self, environment: Environment) -> ComputationalObject:
        o = NIL
        for c in self.sequence:
            o = c.eval(environment)
        return o


class AIf(Analyzer):
    @classmethod
    def adapt(cls, expression: Expression) -> bool:
        return SIf.adapt(expression)

    def __init__(self, expression):
        i = SIf(expression)
        self.cond = analyze(i.condition)
        self.consequence = analyze(i.consequence)
        self.alternative = analyze(i.alternative)

    def eval(self, environment: Environment) -> ComputationalObject:
        if is_true(self.cond.eval(environment)):
            ret = self.consequence.eval(environment)
        else:
            ret = self.alternative.eval(environment)
        return ret


class ALambda(Analyzer):
    @classmethod
    def adapt(cls, expression: Expression) -> bool:
        return SLambda.adapt(expression)

    def __init__(self, expression):
        l = SLambda(expression)
        self.parameter = l.parameter
        self.body = analyze_sequence(l.body)

    def eval(self, environment: Environment) -> ComputationalObject:
        return Procedure(
            parameter=self.parameter,
            body=self.body,
            environment=environment
        )


class AAnd(Analyzer):
    @classmethod
    def adapt(cls, expression: Expression) -> bool:
        return SAnd.adapt(expression)

    def __init__(self, expression):
        self.item_lst = _mp(analyze, SAnd(expression).item_lst)

    def eval(self, environment: Environment) -> ComputationalObject:
        for item in self.item_lst:
            if is_false(item.eval(environment)):
                return Boolean(False)
        return Boolean(True)


class AOr(Analyzer):
    @classmethod
    def adapt(cls, expression: Expression) -> bool:
        return SOr.adapt(expression)

    def __init__(self, expression):
        self.item_lst = _mp(analyze, SOr(expression).item_lst)

    def eval(self, environment: Environment) -> ComputationalObject:
        for item in self.item_lst:
            if is_true(item.eval(environment)):
                return Boolean(True)
        return Boolean(False)


class ACond(Analyzer):
    @classmethod
    def adapt(cls, expression: Expression) -> bool:
        return SCond.adapt(expression)

    def __init__(self, expression):
        self.code = analyze(self._expand(SCond(expression).branch_lst))

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

    def eval(self, environment: Environment) -> ComputationalObject:
        return self.code.eval(environment)


class AApplication(Analyzer):
    @classmethod
    def adapt(cls, expression: Expression) -> bool:
        return SApplication.adapt(expression)

    def __init__(self, expression):
        a = SApplication(expression)
        self.proc = analyze(a.procedure_expression)
        self.arg_lst = _mp(analyze, a.argument_lst)

    def eval(self, environment: Environment) -> ComputationalObject:
        proc = self.proc.eval(environment)
        args = _mp(lambda x: x.eval(environment), self.arg_lst)
        return proc.call(*args)


class ALet(Analyzer):
    @classmethod
    def adapt(cls, expression: Expression) -> bool:
        return SLet.adapt(expression)

    def __init__(self, expression):
        l = SLet(expression)
        self.name_lst = _mp(lambda x: x[0], l.name_value_pair_lst)
        self.value_lst = _mp(lambda x: analyze(x[1]), l.name_value_pair_lst)
        self.body = analyze(l.body)

    def eval(self, environment: Environment) -> ComputationalObject:
        env = environment.extend()
        for name, value in zip(self.name_lst, self.value_lst):
            env.set(name.value, value.eval(environment))
        return self.body.eval(env)


analyzer_class_lst = [
    ASelfEvaluating,
    AVariable,
    AQuoted,
    AAssignment,
    ADefinition,
    ASequence,
    AIf,
    ALambda,
    AAnd,
    AOr,
    ACond,
    ALet,
    AApplication,
]


def _mp(*args, **kwargs):
    return list(map(*args, **kwargs))
