class Transition(BaseException):
    def __init__(self, next_state):
        self.next = next_state

class Statemachine:
    initial_state = None
    state = None
    last_state = None

    def __next__(self):
        if self.state is None:
            assert self.initial_state is not None
            self.state = self.initial_state

        try:
            res = self.state()
            self.last_state = self.state
            return res
        except Transition as next_state:
            self.last_state = self.state
            self.state = next_state.next
            return next(self)
