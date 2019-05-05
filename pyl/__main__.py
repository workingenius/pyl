# -*- coding:utf8 -*-
import sys
from os.path import dirname as d

sys.path.append(d(d(__file__)))

import click

from pyl.repl import repl
from pyl.main import evaluate_sequence
from pyl.parse import parse_sequence


@click.command()
@click.argument('lisp_file',
                type=click.Path(exists=True, file_okay=True, dir_okay=False, readable=True),
                required=False)
def pyl(lisp_file):
    if lisp_file is None:
        repl()
    else:
        with open(lisp_file) as fd:
            evaluate_sequence(parse_sequence(fd.read()))


if __name__ == '__main__':
    pyl()
