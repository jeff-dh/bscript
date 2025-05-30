import random
import bscript

@bscript.task
def toggle():
    yield 0
    yield 1

@bscript.task
def retained_random():
    r = random.random()
    while True:
        yield r

@bscript.task
def retained_choice(choices):
    choice = random.choice(choices)
    while True:
        if choice not in choices:
            choice = random.choice(choices)
        yield choice

@bscript.fsm
class toggleFSM:
    # parameter with type annotations!
    on: int = 1
    off: int = 0

    # internal state(s) without type annotations
    last_state = None

    @bscript.initial_state
    def off_state(self):
        # decision
        if self.last_state == self.off_state:
            raise bscript.Transition(self.on_state)

        # action
        self.last_state = self.off_state
        return self.off

    def on_state(self):
        # decision
        if self.last_state == self.on_state:
            raise bscript.Transition(self.off_state)

        # action
        self.last_state = self.on_state
        return self.on
