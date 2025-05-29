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
    choice = None
    while True:
        if choice is None or choice not in choices:
            choice = random.choice(choices)
        yield choice

@bscript.task
def stubborn_retained_choice(choices):
    choice = None
    while True:
        if choice is None:
            choice = random.choice(choices)
        if not choice in choices:
            print("my choice is gone, still my choice!")
        yield choice

@bscript.fsm
class toggleFSM(bscript.Statemachine):
    def __init__(self, on=1, off=0):
        self.on = on
        self.off = off

    def off_state(self):
        # decision
        if self.last_state == self.state:
            raise self.transition(self.on_state)
        # action
        return self.off

    def on_state(self):
        # decision
        if self.last_state == self.state:
            raise self.transition(self.off_state)
        # action
        return self.on

    initial_state = off_state
