# -*- coding:utf8 -*-

import traceback


from .environment import init_environment
from .evaluator import evaluate
from .parse import parse


def repl():
    env = init_environment()

    while True:
        try:
            inp = raw_input('>> ')
        except EOFError:
            print
            print 'Bye.'
            break

        if inp.strip():
            try:
                expr = parse(inp)
                print evaluate(expr, env)
            except Exception:
                print traceback.format_exc()
