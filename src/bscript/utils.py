from inspect import signature, currentframe

def get_bound_arguments(fsmCls, *args, **kwargs):
    bound_kwargs = signature(fsmCls).bind(*args, **kwargs)
    bound_kwargs.apply_defaults()
    return bound_kwargs.arguments

def optional_arg_decorator(fn):
    def wrapped_decorator(*args, **kwargs):
        if len(args) == 1 and callable(args[0]):
            return fn(args[0])
        else:
            def real_decorator(decoratee):
                return fn(decoratee, *args, **kwargs)
            return real_decorator

    return wrapped_decorator

def get_var_from_parent_frames(name):
    frame = currentframe()

    while frame and not name in frame.f_locals:
        frame = frame.f_back

    if not frame:
        raise RuntimeError()

    return frame.f_locals[name]
