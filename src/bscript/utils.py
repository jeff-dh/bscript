from textwrap import indent
from inspect import currentframe, signature

def get_bound_arguments(f, *args, **kwargs):
    bound_kwargs = signature(f).bind(*args, **kwargs)
    bound_kwargs.apply_defaults()
    return bound_kwargs.arguments

class Tracer:
    def __init__(self):
        self.indent = 0
        self.lines = []
        self.trace_message("-- trace --")

    def __enter__(self):
        self.indent += 1

    def __exit__(self, _exc_type, _exc_val, _exc_tb):
        self.indent -= 1

    def trace_message(self, msg):
        self.lines.append(indent(msg, " " * self.indent * 4))

    def trace_call(self, f, *args, **kwargs):
        bound_kwargs = get_bound_arguments(f, *args, **kwargs)
        f_args = ", ".join(f"{k}={v}" for k, v in bound_kwargs.items())
        self.trace_message(f"{f.__name__}({f_args})")

    def clear(self):
        self.lines = []
        self.trace_message("-- trace --")
        assert self.indent == 0

    def __str__(self):
        return "\n".join(self.lines)

def get_var_from_parent_frames(name):
    frame = currentframe()
    assert frame
    while not name in frame.f_locals:
        frame = frame.f_back
        if not frame:
            msg = f"_get_var_from_parent_frames: can't find variable named {name} in "\
                    "parent frames"
            raise RuntimeError(msg)

    assert frame
    assert name in frame.f_locals
    return frame.f_locals[name]

