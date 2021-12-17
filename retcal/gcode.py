from typing import Union


class Gcode:
    """Generic Gcode command"""

    _command: str
    args: tuple
    params: dict

    def __init__(self, command, *args, **params):
        self._command = command
        self.args = args
        self.params = params

    def __str__(self):
        parts = [self._command]
        parts.extend(self.args)
        parts.extend([f"{key}{value}" for key, value in self.params.items()])

        return " ".join(parts)

class GcodeMotion(Gcode):
    def __init__(self, *args, **params):
        command = getattr(self, "command", "")
        super().__init__(command, *args, **params)

class GcodeRapidMove(GcodeMotion):
    command = "G0"

class GcodeLinearMove(GcodeMotion):
    command = "G1"
    


class Comment:
    """Generic Gcode comment"""

    comment: str

    def __init__(self, comment=""):
        self.comment = comment

    def __str__(self):
        return f";{self.comment}"


TGcode = Union[Gcode, Comment]
