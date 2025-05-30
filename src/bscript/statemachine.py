import inspect

class Transition(BaseException):
    def __init__(self, next_state):
        self.next = next_state

class NoInitialStateFound(BaseException): pass

def initial_state(f):
    f._bscript_initial_state = True
    return f

class Statemachine:
    state = None
    last_state = None

    def _get_initial_state(self):
        for attr_name in self.__dir__():
            attr = getattr(self, attr_name)

            if inspect.ismethod(attr):
                if hasattr(attr, "_bscript_initial_state"):
                    return attr

        raise NoInitialStateFound(self.__class__.__name__)

    def __next__(self):
        if self.state is None:
            self.state = self._get_initial_state()

        try:
            res = self.state()
            self.last_state = self.state
            return res
        except Transition as next_state:
            self.last_state = self.state
            self.state = next_state.next
            return next(self)
