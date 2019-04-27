# -*- coding:utf8 -*-
import sys
from os.path import dirname as d

sys.path.append(d(d(__file__)))

from pyl.repl import repl

repl()
