from inspect import getcallargs, getgeneratorlocals, isgeneratorfunction
from .bts_context import context

class task:
    def __init__(self, generatorfunction):
        assert isgeneratorfunction(generatorfunction)
        self.generatorfunction = generatorfunction
        self.reset()

    @property
    def generator(self):
        return context()._get_state(self, self.generatorfunction)

    def __iter__(self):
        return self.generator

    def reset(self):
        context().reset(self)

    def __call__(self, *args, **kwargs):
        callargs = getcallargs(self.generatorfunction, *args, **kwargs)
        default = lambda: self.generatorfunction(**callargs)

        generator = context()._get_state(self, default)
        getgeneratorlocals(generator).update(callargs)

        try:
            return next(generator)
        except StopIteration as stop:
            self.reset()
            return stop.value
        except Exception:
            self.reset()
            raise
