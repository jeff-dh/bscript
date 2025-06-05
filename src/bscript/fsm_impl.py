from dataclasses import dataclass
from inspect import isclass, ismethod

from .context_impl import context
from .utils import get_bound_arguments, optional_arg_decorator


class Transition(BaseException):
    def __init__(self, next_state):
        self.next = next_state

def initial(fsm_method):
    fsm_method._bscript_initial_state = True
    return fsm_method

class NoInitialStateFound(BaseException): pass


class FSMContext:
    def __init__(self, fsmCls, reset_after_inactivity=False):
        assert isclass(fsmCls)
        self.fsmCls = fsmCls
        self.reset_after_inactivity = reset_after_inactivity
        self.reset()

    def reset(self):
        context().reset_state(self)

    def __call__(self, *args, **kwargs):
        context()._reset_after_inactivity(self)
        callargs = get_bound_arguments(self.fsmCls, *args, **kwargs)

        # get fsm
        def default():
            default = lambda: self._set_initial_state(self.fsmCls(**callargs))
            return context()._get_state(self, default)
        fsm = context()._get_state(self, default)

        # update parameter
        for k, v in callargs.items():
            setattr(fsm, k, v)

        #call
        try:
            match (res := fsm._fsm_state()): # type: ignore
                case Transition():
                    fsm._fsm_state = res.next # type: ignore
                    return self.__call__(**callargs)
                case _:
                    return res
        except StopIteration as stop:
            self.reset()
            return stop.value

    def _set_initial_state(self, fsm):
        for attr_name in fsm.__dir__():
            attr = getattr(fsm, attr_name)

            if ismethod(attr):
                if hasattr(attr, "_bscript_initial_state"):
                    setattr(fsm, "_fsm_state", attr)
                    return fsm

        raise NoInitialStateFound(fsm.__class__.__name__)

@optional_arg_decorator
def fsm(cls, reset_after_inactivity=False):
    return FSMContext(dataclass(cls), reset_after_inactivity)

