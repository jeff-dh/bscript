from inspect import currentframe
from typing import Any

def get_var_from_parent_frames(name):
    frame = currentframe()

    while frame and not name in frame.f_locals:
        frame = frame.f_back

    if not frame:
        raise RuntimeError()

    return frame.f_locals[name]

class bScriptContext:
    def __init__(self):
        self._states = {}
        self.bb = {}

    def execute(_bscript_context_magic, f, *args, **kwargs):
        return f(*args, **kwargs)

    def reset(self, key):
        self._states.pop(key, None)

    def _get_state(self, key, default):
        gen = self._states.get(key, None)
        if gen is None or gen.gi_frame is None:
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
