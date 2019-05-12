"""
exceptioins handler.
"""

class InputError(Exception):
    def __init__(self, ErrorInfo):
        super().__init__(self)
        self.errorinfo = ErrorInfo

    def __repr__(self):
        return self.errorinfo


