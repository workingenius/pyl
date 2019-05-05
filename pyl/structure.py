from typing import List

from pyl.datatype import Expression, Symbol, Pair, NIL, Parameter
from pyl.helpers import list_to_pylist, pylist_to_list, cons_list, first_symbol, by_index


class Structure(object):
    """
    `结构` 可以按照语法把表达式分解成各关键部分，和根据语法把各关键部分组合成表达式

    实现结构与语法的解耦
    """

    def dismantle(self):
        """把完整表达式分解成关键部分"""
        raise NotImplementedError

    def construct(self) -> Expression:
        """用关键部分拼成表达式"""
        raise NotImplementedError

    def __init__(self):
        if getattr(self, 'expression', None):
            self.dismantle()
        else:
            self.expression = self.construct()

    @classmethod
    def adapt(cls, expression: Expression) -> bool:
        return first_symbol(expression) == Symbol(cls.keyword)


class SCondBranch(Structure):
    def __init__(self, expression=None, is_else=None, test=None, then=None):
        self.expression: Expression = expression
        self.is_else: bool = is_else
        self.test: Expression = test
        self.then: Expression = then
        super(self.__class__, self).__init__()

    def dismantle(self):
        self.is_else = self.expression.car == Symbol('else')
        self.test = self.expression.car
        self.then = self.expression.cdr

    def construct(self) -> Expression:
        return Pair(self.test, self.then)


class SQuoted(Structure):
    keyword = 'quote'

    @classmethod
    def adapt(cls, expression: Expression) -> bool:
        return first_symbol(expression) == Symbol(cls.keyword)

    def __init__(self, expression=None, quoted=None):
        self.expression: Expression = expression
        self.quoted: Expression = quoted
        super(self.__class__, self).__init__()

    def dismantle(self):
        self.quoted = self.expression.cdr.car

    def construct(self) -> Expression:
        return Pair(Symbol(self.keyword), Pair(self.quoted, NIL))


class SAssignment(Structure):
    """针对 赋值 的解释"""
    keyword = 'set!'

    @classmethod
    def adapt(cls, expr: Expression) -> bool:
        return first_symbol(expr) == Symbol(cls.keyword)

    def __init__(self, expression=None, variable_name=None, assignment_body=None):
        self.expression: Expression = expression
        self.variable_name: Symbol = variable_name
        self.assignment_body: Expression = assignment_body
        super(self.__class__, self).__init__()

    def dismantle(self):
        self.variable_name = self._variable_name()
        self.assignment_body = self._assignment_body()

    def _variable_name(self) -> str:
        symbol_as_var_name = by_index(self.expression, 1)
        return symbol_as_var_name.value

    def _assignment_body(self) -> Expression:
        body_expr = by_index(self.expression, 2)
        return body_expr

    def construct(self) -> Expression:
        return Pair(Symbol(self.keyword), Pair(self.variable_name, self.assignment_body))


class SDefinition(Structure):
    """针对 define 的解释"""
    keyword = 'define'

    @classmethod
    def adapt(cls, expression: Expression) -> bool:
        return first_symbol(expression) == Symbol(cls.keyword) \
               and isinstance(expression, Pair) \
               and isinstance(by_index(expression, 1), Pair)

    def __init__(self, expression=None, name=None, parameter=None, body=None):
        self.expression: Expression = expression
        self.name: Symbol = name
        self.parameter: Parameter = parameter
        self.body: Expression = body
        super(self.__class__, self).__init__()

    def dismantle(self):
        self.name = self.expression.cdr.car.car
        self.parameter = SParameter(expression=self.expression.cdr.car.cdr).parameter
        self.body = self.expression.cdr.cdr

    def construct(self) -> Expression:
        if not isinstance(self.parameter, Parameter):
            raise TypeError('parameter of definition should be a Parameter')

        return cons_list(Symbol(self.keyword),
                         Pair(self.name, SParameter(parameter=self.parameter).expression),
                         self.body)


class SParameter(Structure):
    def __init__(self, expression=None, parameter=None):
        self.expression: Expression = expression
        self.parameter: Parameter = parameter
        super(self.__class__, self).__init__()

    def dismantle(self):
        self.parameter = Parameter(names=[expr.value for expr in list_to_pylist(self.expression)])

    def construct(self) -> Expression:
        return pylist_to_list(list(map(Symbol, self.parameter.names)))

    @classmethod
    def adapt(cls, expression: Expression) -> bool:
        return isinstance(expression, Pair)


class SSequence(Structure):
    keyword = 'begin'

    def __init__(self, expression=None, sequence=None):
        self.expression: Pair = expression
        self.sequence: Expression = sequence
        super(self.__class__, self).__init__()

    def dismantle(self):
        self.sequence = self.expression.cdr

    def construct(self) -> Expression:
        return Pair(Symbol(self.keyword), self.sequence)


class SIf(Structure):
    keyword = 'if'

    def __init__(self, expression=None, condition=None, consequence=None, alternative=None):
        self.expression: Expression = expression
        self.condition: Expression = condition
        self.consequence: Expression = consequence
        self.alternative: Expression = alternative
        super(self.__class__, self).__init__()

    def dismantle(self):
        self.condition = self.expression.cdr.car
        self.consequence = self.expression.cdr.cdr.car
        self.alternative = self.expression.cdr.cdr.cdr.car

    def construct(self) -> Expression:
        return cons_list(self.condition, self.consequence, self.alternative)


class SLambda(Structure):
    keyword = 'lambda'

    def __init__(self, expression=None, parameter=None, body=None):
        self.expression: Expression = expression
        self.parameter: Parameter = parameter
        self.body: Expression = body
        super(self.__class__, self).__init__()

    def dismantle(self):
        self.parameter = SParameter(self.expression.cdr.car).parameter
        self.body = self.expression.cdr.cdr

    def construct(self) -> Expression:
        return cons_list(Symbol(self.keyword), pylist_to_list(self.parameter), pylist_to_list(self.body))


class SAnd(Structure):
    keyword = 'and'

    def __init__(self, expression=None, item_lst=None):
        self.expression: Expression = expression
        self.item_lst: List[Expression] = item_lst
        super(self.__class__, self).__init__()

    def dismantle(self):
        self.item_lst = list_to_pylist(self.expression.cdr)

    def construct(self) -> Expression:
        return pylist_to_list(self.item_lst)


class SOr(Structure):
    keyword = 'or'

    def __init__(self, expression=None, item_lst=None):
        self.expression: Expression = expression
        self.item_lst: List[Expression] = item_lst
        super(self.__class__, self).__init__()

    def dismantle(self):
        self.item_lst = list_to_pylist(self.expression.cdr)

    def construct(self) -> Expression:
        return pylist_to_list(self.item_lst)


class SCond(Structure):
    keyword = 'cond'

    def __init__(self, expression=None, branch_lst=None):
        self.expression: Expression = expression
        self.branch_lst: List[SCondBranch] = branch_lst
        super(self.__class__, self).__init__()

    def dismantle(self):
        self.branch_lst = list(map(SCondBranch, list_to_pylist(self.expression.cdr)))

    def construct(self) -> Expression:
        return Pair(Symbol(self.keyword), pylist_to_list([c.expression for c in self.branch_lst]))


class SApplication(Structure):
    def __init__(self, expression=None, procedure_expression=None, argument_lst=None):
        self.expression: Expression = expression
        self.procedure_expression: Expression = procedure_expression
        self.argument_lst: List[Expression] = argument_lst
        super(self.__class__, self).__init__()

    def dismantle(self):
        self.procedure_expression = self.expression.car
        self.argument_lst = list_to_pylist(self.expression.cdr)

    def construct(self) -> Expression:
        return Pair(self.procedure_expression, pylist_to_list(self.argument_lst))

    @classmethod
    def adapt(cls, expression: Expression) -> bool:
        return isinstance(expression, Pair)
