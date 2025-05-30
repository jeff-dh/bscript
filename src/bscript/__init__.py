from functools import wraps
from dataclasses import dataclass

from .bscript_context import context, bScriptContext
from .statemachine import Statemachine, Transition, initial_state

def trace(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        context().tracer.trace_call(f, *args, **kwargs)
        with context().tracer:
            return f(*args, **kwargs)
    return wrapper

def trace_message(msg): context().tracer.trace_message(msg)

def _managed_context(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        return context()._call_from_wrapper(f, *args, **kwargs)
    return wrapper

def fsm(cls): return _managed_context(dataclass(cls))
def task(f): return _managed_context(f)
def input(): return context().input
def output(): return context().output
