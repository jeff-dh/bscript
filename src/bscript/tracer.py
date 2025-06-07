from contextlib import contextmanager
from .utils import get_bound_arguments

class Tree:
    def __init__(self, data):
        self.data = data
        self.children = []

    def __repr__(self): return self.data

class Tracer:
    def __init__(self):
        self.reset()

    @property
    def root(self):
        return self.stack[0]

    def reset(self):
        self.stack = [Tree("call-tree")]

    @contextmanager
    def trace_call(self, f, *args, **kwargs):
        bound_kwargs = get_bound_arguments(f, *args, **kwargs)
        f_args = ", ".join(f"{k}={v}" for k, v in bound_kwargs.items())
        msg = f"{f.__name__}({f_args})"

        n = Tree(msg)
        self.stack[-1].children.append(n)
        self.stack.append(n)

        try:
            yield
        finally:
            assert n == self.stack.pop()

    def trace_message(self, msg):
        self.stack[-1].children.append(msg)

    def __repr__(self):
        def print_node(n, fill):
            if n is None:
                n = self.root

            lines = [(f"{fill}|--{n.data}")]
            for c in n.children:
                lines.append(print_node(c, fill + "    "))
            return "\n".join(lines)

        return print_node(self.root, "")
