# -*- coding:utf8 -*-

"""使在 python 中能直观地生成 scheme 列表

不依赖 parser 也能达到 repl 的效果"""
import traceback

from pyl.datatype import Symbol, Number, String, Boolean
from pyl.helpers import pylist_to_list


class Str(str):
    pass


def list_in_python(o):
    if isinstance(o, bool):
        ret = Boolean(o)

    elif isinstance(o, (int, float)):
        ret = Number(o)

    elif isinstance(o, Str):
        ret = String(o)

    elif isinstance(o, str):
        ret = Symbol(o)

    elif isinstance(o, str):
        ret = Symbol(o.encode('utf-8'))

    elif isinstance(o, (tuple, list)):
        ret = pylist_to_list(list(map(list_in_python, o)))

    else:
        raise TypeError('invalid scheme abbreviation')

    return ret


def repl():
    from pyl.environment import init_environment
    from pyl.evaluator import evaluate

    env = init_environment()

    while True:
        try:
            inp = input('!> ')
        except EOFError:
            print()
            print('Bye.')
            break

        if inp.strip():
            try:
                expr = list_in_python(eval(inp))
                print(evaluate(expr, env))
            except Exception:
                print(traceback.format_exc())


if __name__ == '__main__':
    repl()
