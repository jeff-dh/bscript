import bscript

def test_toggle():
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

    assert toggleFSM() == 0
    assert toggleFSM() == 1
    assert toggleFSM() == 0

def test_restart():
    @bscript.fsm
    class restarting_fsm:
        counter = 0

        @bscript.initial_state
        def off_state(self):
            # decision
            if self.counter > 0:
                raise bscript.Transition(self.on_state)

            # action
            self.counter += 1
            return -self.counter

        def on_state(self):
            # decision
            if self.counter > 2:
                raise bscript.Restart()

            # action
            self.counter += 1
            return self.counter

    assert restarting_fsm() == -1
    assert restarting_fsm() == 2
    assert restarting_fsm() == 3
    assert restarting_fsm() == -1
