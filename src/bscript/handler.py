import inspect


class Transition(BaseException):
    def __init__(self, next_state):
        self.next = next_state

class Restart(BaseException): pass

class NoInitialStateFound(BaseException): pass

def initial_state(f):
    f._bscript_initial_state = True
    return f


class TaskHandler:
    def __init__(self, generator):
        self.generator = generator

    def call(self, bound_kwargs):
        # delete generator state if in failure state (frame == None)
        # exception terminated the genrator
        if self.generator.gi_frame is None:
            raise Restart()

        for k, v in bound_kwargs.items():
            self.generator.gi_frame.f_locals[k] = v

        try:
            return next(self.generator)
        except StopIteration:
            raise Restart()


class FSMHandler:
    def __init__(self, fsm):
        self.fsm = fsm
        self.state = self._get_initial_state()

    def _get_initial_state(self):
        for attr_name in self.fsm.__dir__():
            attr = getattr(self.fsm, attr_name)

            if inspect.ismethod(attr):
                if hasattr(attr, "_bscript_initial_state"):
                    return attr

        raise NoInitialStateFound(self.fsm.__class__.__name__)

    def call(self, bound_kwargs):
        for k, v in bound_kwargs.items():
            setattr(self.fsm, k, v)

        try:
            return self.state()
        except Transition as next_state:
            self.state = next_state.next
            return self.call(bound_kwargs)
