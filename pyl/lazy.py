from pyl.datatype import ComputationalObject


class Thunk(ComputationalObject):
    def __init__(self, code, environment):
        self.code = code
        self.env = environment
        self._result = None

    @property
    def result(self):
        if self._result:
            return self._result

        else:
            self._result = self.code.eval(self.env)
            self.env = None
            return self._result

    @staticmethod
    def force(o):
        if isinstance(o, Thunk):
            return o.result
        else:
            return o