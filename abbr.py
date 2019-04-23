# -*- coding:utf8 -*-

u"""使在 python 中能直观地生成 scheme 列表"""


from pyl import Symbol, Number, String, Boolean, pylist_to_list


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

    elif isinstance(o, unicode):
        ret = Symbol(o.encode('utf-8'))

    elif isinstance(o, (tuple, list)):
        ret = pylist_to_list(map(list_in_python, o))

    else:
        raise TypeError('invalid scheme abbreviation')

    return ret


def repl():
    from pyl import evaluate, init_environment

    env = init_environment()

    while True:
        inp = raw_input('')
        expr = list_in_python(eval(inp))
        print evaluate(expr, env)


if __name__ == '__main__':
    repl()
