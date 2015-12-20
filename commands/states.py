"""
    NORMAL = (0, "Represents normal state")
    WAIT = (1, "State after quit received, waiting for yes/no")
    YES = (2, "Quit confirmed with yes")
    NO = (3, "Quit canceled with no")
"""


class State:
    NORMAL = 0
    WAIT = 1
    YES = 2
    NO = 3

    def __init__(self, state, message):
        self.state = state
        self.message = message
