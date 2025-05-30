from typing import Any
import bscript

def test_toggle():
    @bscript.fsm
    class toggle_fsm:
        # parameter with type annotations!
        on: Any = 1
        off: Any = 0

        # internal state(s) without type annotations
        last_state = None

        @bscript.initial_state
        def off_state(self):
            # decision
            if self.last_state == self.off_state:
                return bscript.Transition(self.on_state)

            # action
            self.last_state = self.off_state
            return self.off

        def on_state(self):
            # decision
            if self.last_state == self.on_state:
                return bscript.Transition(self.off_state)

            # action
            self.last_state = self.on_state
            return self.on

    assert toggle_fsm() == 0
    assert toggle_fsm() == 1
    assert toggle_fsm() == 0
    assert toggle_fsm("on", "off") == "on"

def test_pending_transition():
    @bscript.fsm
    class toggle_fsm:
        # parameter with type annotations!
        on: Any = 1
        off: Any = 0

        @bscript.initial_state
        def off_state(self):
            return bscript.PendingTransition(return_value=self.off,
                                             next_state=self.on_state)

        def on_state(self):
            return bscript.PendingTransition(return_value=self.on,
                                             next_state=self.off_state)

    assert toggle_fsm() == 0
    assert toggle_fsm() == 1
    assert toggle_fsm() == 0
    assert toggle_fsm("on", "off") == "on"

def test_restart():
    @bscript.fsm
    class restarting_fsm:
        counter = 0

        @bscript.initial_state
        def off_state(self):
            # decision
            if self.counter > 0:
                return bscript.Transition(self.on_state)

            # action
            self.counter += 1
            return -self.counter

        def on_state(self):
            # decision
            if self.counter > 2:
                return bscript.Restart()

            # action
            self.counter += 1
            return self.counter

    assert restarting_fsm() == -1
    assert restarting_fsm() == 2
    assert restarting_fsm() == 3
    assert restarting_fsm() == -1
