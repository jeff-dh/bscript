from typing import Any
import btscript

def test_basics():
    @btscript.task
    def toggle(on: Any=1, off: Any=0):
        yield off
        yield on

    assert toggle() == 0
    assert toggle() == 1
    assert toggle() == None
    assert toggle("on", "off") == "off"

def test_manual_reset():
    @btscript.task
    def counter():
        i = 0
        while True:
            yield i
            i += 1

    assert counter() == 0
    assert counter() == 1
    counter.reset()
    assert counter() == 0

def test_failure_reset():
    @btscript.task
    def blub():
        yield 0
        raise Exception
        yield 2

    assert blub() == 0
    try:
        blub()
        assert False
    except Exception:
        pass
    assert blub() == 0

def test_return_reset():
    @btscript.task
    def blub():
        yield 0
        return 1
        yield 2

    assert blub() == 0
    assert blub() == 1
    assert blub() == 0

def test_return_reset2():
    @btscript.task
    def blub():
        yield 0
        return
        yield 2

    assert blub() == 0
    assert blub() == None
    assert blub() == 0

# def test_inactive_reset():
#     @btscript.task(reset_after_inactivity=True) #type: ignore
#     def counter():
#         i = 0
#         while True:
#             yield i
#             i += 1
#
#     ctx = btscript.context()
#
#     assert counter() == 0
#     assert counter() == 1
#     ctx.reset_inactive_states()
#     assert counter() == 2
#     ctx.reset_inactive_states()
#     ctx.reset_inactive_states()
#     assert counter() == 0
