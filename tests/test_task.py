from typing import Any
import bscript

def test_basics():
    @bscript.task
    def toggle(on: Any=1, off: Any=0):
        yield off
        yield on

    assert toggle() == 0
    assert toggle() == 1
    assert toggle() == 0
    assert toggle("on", "off") == "on"

def test_restart():
    @bscript.task
    def restart():
        yield 1
        yield 2
        raise bscript.Restart()
        yield 3
        yield 4

    assert restart() == 1
    assert restart() == 2
    assert restart() == 1

def test_inactive_reset():
    @bscript.task
    def counter():
        i = 0
        while True:
            yield i
            i += 1

    ctx = bscript.context()

    assert counter() == 0
    assert counter() == 1
    ctx.reset_inactive_states()
    assert counter() == 2
    ctx.reset_inactive_states()
    ctx.reset_inactive_states()
    assert counter() == 0

def test_manual_reset():
    @bscript.task
    def counter():
        i = 0
        while True:
            yield i
            i += 1

    ctx = bscript.context()

    assert counter() == 0
    assert counter() == 1
    ctx.reset_state(counter)
    assert counter() == 0

