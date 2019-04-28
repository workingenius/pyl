# -*- coding:utf8 -*-

# noinspection PyUnresolvedReferences
try:
    from typing import Optional, List
except ImportError:
    pass

import re

from pyl.base import Expression, NIL, Number, Symbol, String, Boolean, Pair
from pyl.evaluator import EQuoted


# Lisp grammar

# Expression := Primitive | List | Quoted
# Primitive := Number | Symbol | String | Boolean
# List := "(" ")" | "(" Sequence ")"
# Sequence := Expression Sequence | Expression
# Quoted := "`" Expression | "'" Expression

# entrance: Sequence


class ParseError(Exception):
    pass


class Token(object):
    ignore = False

    @property
    def pattern(self):
        raise NotImplementedError

    def is_a(self, kls):
        return isinstance(self, kls)

    def __init__(self, text):
        self.value = text

    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__, self.value)


class TLeftPar(Token):
    pattern = re.compile(r'\(')
    value = '('


class TRightPar(Token):
    pattern = re.compile(r'\)')
    value = ')'


class TQuoteMark(Token):
    pattern = re.compile(r"\'|`")
    value = "'"


class TNumber(Token):
    pattern = re.compile(r'-?\d+(\.\d*)?')

    def __init__(self, text):
        try:
            num = int(text)
        except ValueError:
            num = float(text)
        self.value = num


class TString(Token):
    pattern = re.compile(r'".*?"')  # TODO: check scheme string escape

    def __init__(self, text):
        self.value = text.strip('"')


class TSymbol(Token):
    pattern = re.compile(r'[^()\s]+')

    def __init__(self, text):
        self.value = text


class TBoolean(Token):
    pattern = re.compile(r'#t|#f')

    def __init__(self, text):
        self.value = False if 'f' in text else True


class TBlank(Token):
    pattern = re.compile(r'\s+')
    ignore = True


class TComments(Token):
    pattern = re.compile(r';.*\n')
    ignore = True


class TEof(Token):
    pattern = re.compile(r'')

    def __repr__(self):
        return 'TEof()'


EOF = TEof(None)

token_by_preference = [
    TBlank,
    TComments,
    TLeftPar,
    TRightPar,
    TQuoteMark,
    TNumber,
    TString,
    TBoolean,
    TString,
    TSymbol,
]


def tokenize(text):
    rest = text

    while rest:
        for token_class in token_by_preference:
            match = token_class.pattern.match(rest)

            if match:
                rest = rest[match.end():]
                if not token_class.ignore:
                    yield token_class(match.group())
                break
        else:
            raise ParseError('tokenize error')

    yield EOF


class Parser(object):
    def __init__(self, token_lst):
        self.token_lst = iter(token_lst)
        self.buffer = []

    def foresee(self, number=1):
        assert number >= 1

        dif = number - len(self.buffer)

        # want to see more from token list, then pre-read tokens and save to buffer
        if dif > 0:
            for i in range(dif):
                try:
                    tok = next(self.token_lst)
                except StopIteration:
                    self.error('too early EOF')
                else:
                    self.buffer.append(tok)

        if number == 1:
            return self.buffer[0]
        elif number > 1:
            return self.buffer[:number]

    def cut(self, number=1):
        ret = self.foresee(number)
        self.buffer = self.buffer[number:]
        return ret

    def parse_number(self):
        t = self.foresee()
        if t.is_a(TNumber):
            self.cut()
            return Number(t.value)

    def parse_symbol(self):
        t = self.foresee()
        if t.is_a(TSymbol):
            self.cut()
            return Symbol(t.value)

    def parse_string(self):
        t = self.foresee()
        if t.is_a(TString):
            self.cut()
            return String(t.value)

    def parse_boolean(self):
        t = self.foresee()
        if t.is_a(TBoolean):
            self.cut()
            return Boolean(t.value)

    def parse_primitive(self):
        return self.parse_number() or self.parse_symbol() or self.parse_string() or self.parse_boolean()

    def parse_quoted(self):
        tok = self.foresee()
        if tok.is_a(TQuoteMark):
            self.cut()  # cut quote mark
            exp = self.parse_expression()
            return EQuoted(quoted=exp).expression

    def parse_list(self):
        t1 = self.foresee()
        if t1.is_a(TLeftPar):

            t1, t2 = self.foresee(2)
            if t2.is_a(TRightPar):  # "()" met
                self.cut(2)
                return NIL

            else:
                self.cut()  # cut (
                seq = self.parse_sequence()

                t = self.foresee()
                if not t.is_a(TRightPar):
                    self.error('a closing right parenthesis wanted')
                self.cut()  # cut )

                return seq

    def parse_sequence(self):
        car = self.parse_expression()
        if not car:
            return None

        cdr = self.parse_sequence()
        if not cdr:
            return Pair(car, NIL)
        else:
            return Pair(car, cdr)

    def parse_expression(self):
        pri = self.parse_primitive()
        if pri is not None:
            return pri

        lis = self.parse_list()
        if lis is not None:
            return lis

        quo = self.parse_quoted()
        if quo is not None:
            return quo

    def parse(self):
        exp = self.parse_sequence()
        if exp is None:
            self.error('an expression sequence wanted')
        if not self.cut().is_a(TEof):
            self.error('extra code met')
        return exp

    def error(self, message):
        raise ParseError(message)


def parse(code: Optional[str] = None, token_lst: Optional[List[Token]] = None) -> Expression:
    token_lst = token_lst or tokenize(code)
    return Parser(token_lst).parse_expression()


def parse_sequence(code: Optional[str] = None, token_lst: Optional[List[Token]] = None) -> Expression:
    token_lst = token_lst or tokenize(code)
    return Parser(token_lst).parse()


# sample_code = '''
# `(1 2)
#
# (define (add x y) (+ x y))
#
# ;;;a variable in current scope
# (set! bb "kdkdkdk")  ; named bb
#
# (print (add 4 5))
#
# (newline)
#
# '''
#
# # for t in tokenize(sample_code):
# #     print t
#
#
# print parse(sample_code)
