from typing import Any, Generator

from .utils import get_var_from_parent_frames,\
                   get_bound_arguments,\
                   Tracer

class bScriptContext:
    def __init__(self):
        self._states = {}
        self._active_states = set()

        self.input: Any = None
        self.output: Any = None

        self.tracer = Tracer()

    def _call_from_wrapper(self, func_or_fsm, *args, **kwargs):
        # mark as active
        self._active_states.add(func_or_fsm)

        # create state if necessary
        if not func_or_fsm in self._states:
            self._states[func_or_fsm] = func_or_fsm(*args, **kwargs)
        state = self._states[func_or_fsm]

        # bind parameters into frames / fsm
        bound_kwargs = get_bound_arguments(func_or_fsm, *args, **kwargs)
        for k, v in bound_kwargs.items():
            if isinstance(state, Generator):
                state.gi_frame.f_locals[k] = v
            else:
                setattr(state, k, v)

        # call next on state
        with self.tracer:
            self.tracer.trace_call(func_or_fsm, *args, **kwargs)
            try:
                return next(state)
            except StopIteration:
                del self._states[func_or_fsm]
                return self._call_from_wrapper(func_or_fsm, *args, **kwargs)

    def reset_inactive_states(self):
        self._states = {k:v for k, v in self._states.items()
                        if k in self._active_states}
        self._active_states.clear()

    def call(self, f, *args, **kwargs):
        _bscript_context = self
        _bscript_context = _bscript_context # avoid unused

        return f(*args, **kwargs)

    def frame(self, root_skill, *args, **kwargs):
        self.reset_inactive_states()
        self.tracer.clear()
        self.call(root_skill, *args, **kwargs)

_defaultContext = bScriptContext()

def context():
    try:
        return get_var_from_parent_frames("_bscript_context")
    except RuntimeError:
        return _defaultContext
