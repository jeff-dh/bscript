import inspect
from typing import Any
from undecorated import undecorated

from .utils import get_var_from_parent_frames,\
                   get_bound_arguments,\
                   Tracer

from .handler import FSMHandler, TaskHandler, Restart

class bScriptContext:
    def __init__(self):
        self._states = {}
        self._active_states = set()

        self.input: Any = None
        self.output: Any = None

        self.tracer = Tracer()

    def _call(self, func_or_fsm, *args, **kwargs):
        self._active_states.add(func_or_fsm)
        bound_kwargs = get_bound_arguments(func_or_fsm, *args, **kwargs)

        Handler = TaskHandler if not inspect.isclass(func_or_fsm) else FSMHandler

        if not func_or_fsm in self._states:
            self._states[func_or_fsm] = Handler(func_or_fsm(*args, **kwargs))
        handler = self._states[func_or_fsm]

        with self.tracer.trace_call(func_or_fsm, *args, **kwargs):
            try:
                return handler.call(bound_kwargs)
            except Restart:
                self.reset_state(func_or_fsm)
                return self._call(func_or_fsm, *args, **kwargs)

    def reset_inactive_states(self):
        self._states = {k:v for k, v in self._states.items()
                        if k in self._active_states}
        self._active_states.clear()

    def execute(self, f, *args, **kwargs):
        # this sets the context which gets fetch from this frame
        # -> context()
        _bscript_context = self
        _bscript_context = _bscript_context # avoid unused

        return f(*args, **kwargs)

    def reset_state(self, func_or_fsm):
        f = undecorated(func_or_fsm)
        if f in self._states:
            del self._states[f]

_defaultContext = bScriptContext()

def context():
    try:
        return get_var_from_parent_frames("_bscript_context")
    except RuntimeError:
        return _defaultContext
