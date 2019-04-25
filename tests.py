# -*- coding:utf8 -*-
import unittest

from abbr import list_in_python as l
from pyl.base import Number, String, Boolean
from pyl.main import evaluate


class TestSelfEvaluating(unittest.TestCase):
    def test_number(self):
        self.assertEqual(evaluate(Number(1)), Number(1))

    # def test_symbol(self):
    #     self.assertEqual(evaluate(Symbol('a')), Symbol('a'))

    def test_string(self):
        self.assertEqual(evaluate(String('b')), String('b'))

    def test_boolean(self):
        self.assertEqual(evaluate(Boolean(True)), Boolean(True))
        self.assertEqual(evaluate(Boolean(False)), Boolean(False))


class TestQuoted(unittest.TestCase):
    def test_quoted(self):
        self.assertEqual(
            evaluate(
                l(['quote', [1, 2, 3]])
            ),
            l([1, 2, 3])
        )


class TestLambda(unittest.TestCase):
    def test_lambda(self):
        self.assertEqual(
            evaluate(
                l([['lambda', ['x', 'y'], ['+', 'x', 'y']], 1, 2])
            ),
            Number(3)
        )


class TestBoolean(unittest.TestCase):
    def test_and(self):
        self.assertEqual(
            evaluate(
                l(['and', True, False])
            ),
            Boolean(False)
        )
