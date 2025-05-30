from functools import wraps as _wraps
from dataclasses import dataclass as _dataclass

from .bscript_context import context, bScriptContext
from .handler import Transition, PendingTransition, initial_state, Restart

def trace(f):
    @_wraps(f)
    def wrapper(*args, **kwargs):
        with context().tracer.trace_call(f, *args, **kwargs):
            return f(*args, **kwargs)
    return wrapper

def trace_message(msg): context().tracer.trace_message(msg)

def _managed_context(f):
    @_wraps(f)
    def wrapper(*args, **kwargs):
        return context()._call(f, *args, **kwargs)
    return wrapper

def fsm(cls): return _managed_context(_dataclass(cls))
def task(f): return _managed_context(f)
def input(): return context().input
def output(): return context().output
