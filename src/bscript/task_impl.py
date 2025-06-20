from inspect import getcallargs, getgeneratorlocals, isfunction, isgeneratorfunction

from .context_impl import context, tracer
from .utils import optional_arg_decorator

class TaskContext:
    def __init__(self, generatorfunction, reset_after_inactivity=False):
        assert isgeneratorfunction(generatorfunction)
        self.generatorfunction = generatorfunction
        self.reset_after_inactivity = reset_after_inactivity
        self.reset()

    def reset(self):
        context().reset_state(self)

    def __call__(self, *args, **kwargs):
        context()._reset_after_inactivity(self)
        callargs = getcallargs(self.generatorfunction, *args, **kwargs)

        # get generator
        default = lambda: self.generatorfunction(**callargs)
        generator = context()._get_state(self, default)

        # update parameter
        getgeneratorlocals(generator).update(callargs)

        # call
        try:
            with tracer().trace_call(self.generatorfunction, *args, **kwargs):
                return next(generator)
        except StopIteration as stop:
            self.reset()
            return stop.value
        except Exception:
            self.reset()
            raise

def traced(f):
    def wrapper(*args, **kwargs):
        with tracer().trace_call(f, *args, **kwargs):
            return f(*args, **kwargs)
    return wrapper

@optional_arg_decorator
def task(f, reset_after_inactivity=False):
    if isgeneratorfunction(f):
        return TaskContext(f, reset_after_inactivity)
    else:
        assert isfunction(f)
        return traced(f)
