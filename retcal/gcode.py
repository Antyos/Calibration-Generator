from typing import Union


# Generic Gcode


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


class GcodeCommand(Gcode):
    def __init__(self, *args, **params):
        command = getattr(self, "command", "")
        super().__init__(command, *args, **params)


# Specific Gcode


class GcodeRapidMove(GcodeCommand):
    """G0: Rapid move."""
    command = "G0"


class GcodeLinearMove(GcodeCommand):
    """G1: Linear move."""
    command = "G1"


class GcodeUseAbsolutePositioning(GcodeCommand):
    """G90: Use Absolute positioning."""
    command = "G90"


class GcodeUseIncrementalPositioning(GcodeCommand):
    """G91: Use incremental positioning."""
    command = "G91"


class GcodeSetPosition(GcodeCommand):
    """G92: Set position."""
    command = "G92"


# Misc Gcode


class GcodeMisc(Gcode):
    """Miscellaneous Gcode"""

    gcode: str

    def __init__(self, gcode: str):
        self.gcode = gcode

    def __str__(self):
        return self.gcode


# Comments


class Comment:
    """Generic Gcode comment"""

    comment: str

    def __init__(self, comment=""):
        self.comment = comment

    def __str__(self):
        return f";{self.comment}"


# Typing

TGcode = Union[Gcode, Comment]
