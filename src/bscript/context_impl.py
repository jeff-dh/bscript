from typing import Any, Generator
from .utils import get_var_from_parent_frames

class bScriptContext:
    def __init__(self):
        self._states = {}
        self.bb = {} # blackboard
        self.input: Any = None
        self.output: Any = None
        self._active_states = set()
        self._last_active_states = set()

    def execute(_bscript_context_magic, f, *args, **kwargs):
        return f(*args, **kwargs)

    def reset_state(self, key):
        self._states.pop(key, None)

    def _reset_after_inactivity(self, key):
        if not key.reset_after_inactivity:
            return

        self._active_states.add(key)
        if not key in self._last_active_states:
            self.reset_state(key)
            self._last_active_states.add(key)

    def reset_inactive_states(self):
        self._last_active_states = self._active_states.copy()
        self._active_states.clear()

    def _get_state(self, key, default):
        gen = self._states.get(key, None)
        if gen is None or (isinstance(gen, Generator) and gen.gi_frame is None):
            gen = default()
            self._states[key] = gen
        return gen

_default_context = bScriptContext()

def context():
    try:
        return get_var_from_parent_frames("_bscript_context_magic")
    except RuntimeError:
        return _default_context

def bb(): return context().bb
def input(): return context().input
def output(): return context().output
