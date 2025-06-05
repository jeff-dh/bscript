# bscript

[![PyPI - Version](https://img.shields.io/pypi/v/bscript.svg)](https://pypi.org/project/bscript)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/bscript.svg)](https://pypi.org/project/bscript)

-----

## bscript

`bscript` is a python behavior specification library for agents respectively
robots. It is similar to hierarchical finite state machines, but primarily uses
decorated python generators -- called _tasks_ -- instead of finite state
machines. This provides an imperative scripting like approach to behavior
engineering.

_tasks_ are callable _singletons_ which wrap a generator and can be called like
regular functions:

```python
@task
def foo():
    yield 1
    return 2

assert foo() == 1
assert foo() == 2
assert foo() == 1
```

These "_state based functions_" can be used to describe complex and deliberate
hierarchical behaviors:

```python
@task
def eat():
    try:
        while peel_banana(): yield Running
        while eat_banana(): yield Running
    except Failure:
        while eat_apple(): yield Running

    # implicit return Success
```

## Table of Contents

- [Installation](#installation)
- [Basics](#Basics)
    - [actions - low level behaviors](#actions)
    - [high level behaviors](#high-level-behaviors)
        - [sequence of sub behaviors](#sequence-of-sub-behaviors)
        - [failures and faillbacks](#failures-and-fallbacks)
        - [parallel execution of behaviors](#parallel-execution-of-behaviors)
        - [conditions](#conditions)
        - [conditional parallel execution](#conditional-parallel-execution)
- [how this works](#how-this-works)
    - [`task`](#tasks)
    - [`Running` & `Success`](#running--success)
- [Examples](#Examples)
- [License](#license)


## Installation

```console
# only available for python >= 3.13
pip install bscript
```

## Basics

- a node is usually a _task_ -- which is a superset of a function
    - (finite state machine-ish nodes are also available)
- each node in the hierarchy should usually return either `Running` (`== True`) or `Success` (`== None`)
- when a node finishes its execution without returning or yielding a value, it implicitly returns `None` (`== Success`)
- a `Failure` is an exception and must be raised (and caught)

### actions

low level nodes that execute actions can often be written as functions:

```python
@task
def drive_to(target):
    output().target = target
    return Success if target_reached(target) else Running
```

or as a generator:

```python
@task
def drive_to(target):
    while not target_reached(target):
        output().target = target
        yield Running

    # Success (implicit return None / Success)
```


### high level behaviors

#### sequence of sub behaviors

```python
@task
def eat():
    while peel_banana(): yield Running
    while eat_banana(): yield Running

    # Success (implicit return None / Success)
```

#### failures and fallbacks

```python
@task
def eat():
    try:
        while peel_banana(): yield Running
        while eat_banana(): yield Running
    except Failure:
        while eat_apple(): yield Running
```

#### parallel execution of behaviors

```python
@task
def walk_to_bus_stop():
    while walk_to(next_bus_stop()):
        listen_to_music()
        eat_an_apple()
        yield Running
```

#### conditions

```python
@task
def emergency():
    # callers can make decisions based on whether this task is Running or not
    if random() > 0.9:
        yield Running
        yield Running # always running for 2 frames in a row

@task
def some_behavior():
    if emergency():
        run_away()
        return Running
    else:
        return do_something()
```

#### conditional parallel execution

```python
@task
def attend_talk():
    while listen_to_talk():
        if new_message():
            read_message()
        elif hungry():
            eat_an_apple()
        yield Running
```

## how this works


### tasks

_tasks_ are generators -- a superset of functions -- that can be called like
functions. They are implemented as callable _singeltons_ and update their
parameters (local variables inside the generator namespace). A `StopIteration`
is transformed into a `return` statement like behavior.

A _task_ is pretty much a "function with an internal state" or a "function
with `yield` statements".

`yield` and `return` statements can be mixed inside python generators -- and
therefor inside _tasks_ aswell. They behave as expected:

- `yield` returns a value and resumes the execution
- `return` returns a value and restarts the execution

the result is pretty similar to functions:

```python
from bscript import task

@task
def foo_pass():
    pass
    # implicit return None, like regular functions

assert foo_pass() == None

@task
def foo_return():
    return 1

assert foo_return() == 1

@task
def foo_yield():
    yield 1
    # implicit return None

assert foo_yield() == 1
assert foo_yield() == None
assert foo_yield() == 1

@task
def foobar():
    yield 1
    yield 2
    return 99
    yield 4

assert foobar() == 1
assert foobar() == 2
assert foobar() == 99
assert foobar() == 1

@task
def foox(x):
    yield x
    yield x

assert foox(4) == 4
assert foox(9) == 9
assert foox(1) == None
```

### `Running` & `Success`

`bscript` defines the states `Running` and `Success`. It turns out defining
them like this...

```python
Running = True
Success = None
```

...has pretty interesting properties, especially since each function or _task_
always returns something -- explicitly or implicitly `None`:

```python
assert True is Running is not Success
assert None is Success is not Running

def always_successful():
    pass
    # implicit return None / Success

def always_running():
    return Running

assert always_successful() is Success
assert always_successful() is not Running

assert always_running() is Running
assert always_running() is not Success
```

### `while` and `if` in combination with `Running` & `Success`

- `while do_something():` is equivalent to
    - `while do_something() is Running:`
    - `while do_something() is not Success:`

- `if something():` is equivalent to:
    - `if something() is Running:`
    - `if something() is not Success:`


### finite state machin-ish nodes, context handling, input & output and more

-> [docs/details.md](https://github.com/jeff-dh/bscript/blob/main/docs/details.md)


## Examples

The [lunch
behavior](https://github.com/jeff-dh/bscript/blob/main/examples/have_lunch.py)
and the [irsim
behavior](https://github.com/jeff-dh/bscript/blob/main/examples/irsim/behavior.py)
show basic example applications.


## License

`bscript` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
