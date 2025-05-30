# bscript

[![PyPI - Version](https://img.shields.io/pypi/v/bscript.svg)](https://pypi.org/project/bscript)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/bscript.svg)](https://pypi.org/project/bscript)

-----

## Table of Contents

- [bscript](#bscript)
- [Installation](#Installation)
- [Examples](#Examples)
- [License](#license)

## bscript

Only works with `python>=3.13`.

`bscript` is a behavior specification library for agents respectively robots.
It is similar to other hierarchical finite state machine approaches, but
extends the hierarchy with (python) generators (called _tasks_). `bscript`
tries to enable a scripting like approach to behavior engineering in contrast
to restricted finite state machines solutions.

_Tasks_ -- as well as state machines -- can be called like regular functions.
This is achieve by using an implicit context management for the _tasks_ and
state machines.

_Tasks_ and state machines have the following (additional) properties:

- implicit context management (kind of singletons, like functions)
- parameters are manipulated and get updated at each call (not only at the
  creation of the generator context)
- the generators are restartet imediately if a `StopIteration` occurs (or a
  `bscript.Restart()` exceptoin was thrown)

The result are generators (_tasks_) and state machines which can be called like
regular functions and whose parameters (might) change from call to call. These
"_state based functions_" can be used to describe hierarchical agent / robot
behaviors.

### a task toggle example

```python
>>> import bscript
>>>
>>> @bscript.task
... def toggle(on=1, off=0):
...     yield off
...     yield on
...
>>> toggle()
0
>>> toggle()
1
>>> toggle("on", "off")
'off'
>>> toggle()
1
```

## Installation

```console
pip install bscript@git+https://github.com/jeff-dh/bscript
```

## Examples

### retained choice

a basic decision task

 ```python
>>> import random
>>> import bscript
>>>
>>> @bscript.task
... def retained_choice(choices):
...     choice = random.choice(choices)
...     while True:
...         if choice not in choices:
...             choice = random.choice(choices)
...         yield choice
...
>>> retained_choice([1, 2, 3])
1
>>> retained_choice([1, 2, 3])
1
>>> retained_choice([2, 3])
3
>>> retained_choice([2, 3])
3
>>> retained_choice([1, 2, 3, 4, 5])
3
>>> retained_choice([4, 5, 6])
4
```

### statemachines

a finite state machine that toggles between two states

```python
>> import bscript
>>>
>>> @bscript.fsm
... class toggleFSM:
...     # parameter with type annotations!
...     on: int = 1
...     off: int = 0
...
...     # internal state(s) without type annotations
...     last_state = None
...
...     @bscript.initial_state
...     def off_state(self):
...         # decision
...         if self.last_state == self.off_state:
...             raise bscript.Transition(self.on_state)
...
...         # action
...         self.last_state = self.off_state
...         return self.off
...
...     def on_state(self):
...         # decision
...         if self.last_state == self.on_state:
...             raise bscript.Transition(self.off_state)
...
...         # action
...         self.last_state = self.on_state
...         return self.on
...
>>> toggleFSM()
0
>>> toggleFSM()
1
>>> toggleFSM()
0
>>> toggleFSM("on", "off")
'on'
```

### hierarchical behaviors

_tasks_, finite state machines and regular functions can be arbitrarily mixed
to complex hierarchical behaviors. All three can be called likes functions and can
return values, raise exceptions, execute arbitrary code.....

```python
>>> import bscript
>>>
>>> @bscript.fsm
... class fsm_behavior:
...     @bscript.initial_state
...     def blub(self):
...         print("fsm behavior")
...
>>> def func_behavior():
...     print("stateless behavior")
...
>>> @bscript.task
... def root_behavior():
...     yield func_behavior()
...     yield fsm_behavior()
...
>>> root_behavior()
stateless behavior
>>> root_behavior()
fsm behavior
```

### implicit context

If no context is explicitly specified the default context will be used which is accessible through `bscript.context()`.

### custom & multiple context

```python
>>> import bscript
>>>
>>> ctx1 = bscript.bScriptContext()
>>> ctx2 = bscript.bScriptContext()
>>>
>>> @bscript.task
... def toggle():
...     yield 0
...     yield 1
...
>>> ctx1.call(toggle)
0
>>> ctx2.call(toggle)
0
>>> toggle()
0
>>> ctx1.call(toggle)
1
>>> ctx2.call(toggle)
1
>>> toggle()
1
```

### input & output

global `input` (world model) and `output` (action selection) are available through the `context`:

```python
>>> import bscript
>>>
>>> ctx = bscript.context()
>>> ctx.input = 5 # -> world model
>>> ctx.output = {} # -> action selection
>>>
>>> # run behaviors, call bscript.input() / bscript.output() from anywhere
>>> def foo():
...     bscript.output()["double"] = bscript.input() * 2
...
>>> foo()
>>> ctx.output
{'double': 10}
```

### manual resting states

```python
>>> import bscript
>>>
>>> @bscript.task
... def counter():
...     for i in range(99):
...         yield i
...
>>> ctx = bscript.context()
>>>
>>> counter()
0
>>> counter()
1
>>> ctx.reset_state(counter)
>>> counter()
0
```

### reseting inactivity states

as other behavior speicification languages bscript can reset
"inactive" _tasks_ (and state machines) with
`context.reset_inactive_states()`. A _task_ (or state machine) is
considered inactive if it was not called since the last call to
`reset_inactive_states` (or since the start of the program).

```python
>>> import bscript
>>>
>>> @bscript.task
... def counter1():
...     for i in range(99):
...         yield i
...
>>> @bscript.task
... def counter2():
...     for i in range(99):
...         yield i
...
>>>
>>> ctx = bscript.context()
>>>
>>> counter1()
0
>>> counter2()
0
>>> ctx.reset_inactive_states()
>>> counter1()
1
>>> counter2()
1
>>> ctx.reset_inactive_states()
>>> counter2()
2
>>> ctx.reset_inactive_states()
>>> counter1() # restarted because was inactive in last frame
0
>>> counter2() # continuing because was active all the time
3
>>>
```

TODO: make this optional per task

### tracer

for debugging purpose `bscript` includes a tracer:

```python
>>> import bscript
>>>
>>> @bscript.trace
... def foo(a, b, c):
...     bscript.trace_message("inside foo")
...
>>> @bscript.task
... def bar(a, b, c):
...     yield foo(2*a, 2*b, 2*c)
...
>>> bar(1, 2, 3)
>>> ctx = bscript.context()
>>> print(ctx.tracer.format())
bar(a=1, b=2, c=3)
    foo(a=2, b=4, c=6)
        inside foo
```

the `task` and `fsm` decorators include a call to `bscript.trace`.

use `ctx.tracer.clear()` to clear the tracer before the next frame.


## License

`bscript` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
