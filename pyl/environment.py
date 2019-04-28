# -*- coding:utf8 -*-


from typing import Optional, Any


class EnvironmentFrame(object):
    def __init__(self, parent: Optional['Environment'] = None):
        self.data = {}
        self.parent: Optional[Environment] = parent

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

    def get(self, key: str) -> Any:
        return self.frame.get(key)

    def set(self, key: str, value: Any):
        self.frame.set(key, value)

    def extend(self) -> 'Environment':
        return Environment(EnvironmentFrame(parent=self.frame))


def init_environment() -> Environment:
    """初始环境"""
    env = Environment()

    from .primitive import primitives

    for primitive in primitives:
        env.set(primitive.keyword, primitive)

    return env
