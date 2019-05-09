# -*- coding:utf8 -*-
import sys
from os.path import dirname as d

sys.path.append(d(d(__file__)))

import click

from pyl.repl import repl
from pyl.main import Evaluator
from pyl.parse import parse_sequence


@click.command()
@click.argument('lisp_file',
                type=click.Path(exists=True, file_okay=True, dir_okay=False, readable=True),
                required=False)
@click.option('--analyze/--no-analyze', '-a/-A', 'analyze_or_not', default=True, help='analyze before evaluation or not')
def pyl(lisp_file, analyze_or_not):
    if lisp_file is None:
        repl(bool_analyze=analyze_or_not)
    else:
        with open(lisp_file) as fd:
            Evaluator(bool_analyze=analyze_or_not).eval_seq(
                parse_sequence(fd.read())
            )


if __name__ == '__main__':
    pyl()
