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
class toggleFSM(bscript.Statemachine):
    def __init__(self, on=1, off=0):
        self.on = on
        self.off = off

    @bscript.initial_state
    def off_state(self):
        # decision
        if self.last_state == self.state:
            raise bscript.Transition(self.on_state)
        # action
        return self.off

    def on_state(self):
        # decision
        if self.last_state == self.state:
            raise bscript.Transition(self.off_state)
        # action
        return self.on
