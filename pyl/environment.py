# -*- coding:utf8 -*-


try:
    # noinspection PyUnresolvedReferences
    from typing import List, Optional, Union, Dict, Type, Callable, Any
except ImportError:
    pass


class EnvironmentFrame(object):
    def __init__(self, parent=None):
        self.data = {}
        self.parent = parent  # type: Optional[Environment]

    def get(self, key):
        if key in self.data:
            return self.data[key]
        elif self.parent:
            return self.parent.get(key)

    def set(self, key, value):
        self.data[key] = value


class Environment(object):
    def __init__(self, frame=None):
        self.frame = frame or EnvironmentFrame()

    def get(self, key):
        # type: (str) -> Any
        return self.frame.get(key)

    def set(self, key, value):
        # type: (str, Any) -> None
        self.frame.set(key, value)

    def extend(self):
        # type: () -> Environment
        return Environment(EnvironmentFrame(parent=self.frame))


def init_environment():
    u"""初始环境"""
    env = Environment()

    from primitive import primitives

    for primitive in primitives:
        env.set(primitive.keyword, primitive)

    return env
