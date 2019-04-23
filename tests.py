# -*- coding:utf8 -*-
from pyl import Symbol, Number, String, Boolean
from pyl import evaluate
from pyl import EvaluatorSyntaxError
from abbr import list_in_python as l
import unittest


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

    def test_bad_quoted(self):
        with self.assertRaises(EvaluatorSyntaxError):
            evaluate(
                l(['quote'])
            )
