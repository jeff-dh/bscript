from .task_context import task
from .bts_context import bScriptContext, context, input, output
from .fsm_context import fsm, initial, NoInitialStateFound, Transition

Running = True
Success = None

class Failure(Exception): pass

from itertools import chain as sequence

def fallback(*tasks):
    for t in tasks:
        try:
            yield from t
            return
        except Failure:
            pass

    raise Failure()

__all__ = ["task", "bScriptContext", "context", "input", "output",
           "fsm", "initial", "NoInitialStateFound", "Transition",
           "Running", "Success", "Failure",
           "sequence", "fallback"]
