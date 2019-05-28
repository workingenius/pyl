# -*- coding:utf8 -*-

import traceback

from pyl.lazy import Thunk
from pyl.main import Evaluator
from .parse import parse, tokenize, TLeftPar, TRightPar


def is_par_completed(token_lst):
    par_stack = 0

    for tok in token_lst:
        if tok.is_a(TLeftPar):
            par_stack += 1
        elif tok.is_a(TRightPar):
            par_stack -= 1
            if par_stack < 0:
                return True

    return par_stack <= 0


def repl(bool_analyze):
    evaluator = Evaluator(bool_analyze)

    exp_buffer = ''
    has_prompt = True

    while True:
        try:
            inp = input('>> ' if has_prompt else '')
        except (EOFError, KeyboardInterrupt):
            print()
            print('Bye.')
            break

        if inp.strip():
            exp_buffer += (' ' + inp)

            try:
                token_lst = tokenize(exp_buffer)
                if is_par_completed(token_lst):
                    expr = parse(exp_buffer)
                    exp_buffer = ''
                    has_prompt = True
                    print(Thunk.force(evaluator.eval(expr)))

                else:
                    has_prompt = False

            except Exception:
                print(traceback.format_exc())
