from retcal.calibration_header import generate_header
from retcal.calibration_tower import layer_group
from retcal.config import GcodeConfig
from retcal.gcode import (
    Comment,
    Gcode,
    GcodeLinearMove,
    GcodeMisc,
    GcodeRapidMove,
    GcodeSetPosition,
    GcodeUseAbsolutePositioning,
    GcodeUseIncrementalPositioning,
    TGcode,
)


def start_gcode(config) -> list[TGcode]:
    """Gcode to start a print"""
    return [
        Comment("Start Gcode"),
        Gcode("M140", S=int(config.bed_temp)),
        Gcode("M105"),
        Gcode("M190", S=int(config.bed_temp)),
        Gcode("M104", S=int(config.hotend_temp_init)),
        Gcode("M105"),
        Gcode("M109", S=int(config.hotend_temp_init)),
        Gcode("M82"),
        Gcode("G28"),
        GcodeSetPosition(E=0),
        GcodeLinearMove(F=200, E=1),
        GcodeSetPosition(E=0),
        GcodeMisc(config.custom_gcode),
        Comment(),
        Comment(),
    ]


def raft_gcode(config: GcodeConfig) -> list[TGcode]:
    """Generate raft Gcode"""
    xpos = config.bed_shape_x / 2 - 30
    ypos = config.bed_shape_y / 2 - 30
    zpos = config.layer_height
    # Overextruding Raft
    e_raft = config.get_e_value(60)

    gcode: list[TGcode] = [
        Comment("Start Movement"),
        Comment(),
        GcodeUseAbsolutePositioning(),
        GcodeLinearMove("G1", Z=2),
        GcodeLinearMove("G1", F=config.travel_speed, X=xpos, Y=ypos, Z=zpos),
        GcodeUseIncrementalPositioning(),
        Comment(),
    ]

    # Horizontal part of raft
    gcode.append(Comment("Layer 1"))
    for _ in range(30):
        gcode.extend(
            [
                GcodeLinearMove(F=config.print_speed // 2, X=60, E=e_raft),
                GcodeRapidMove(F=config.travel_speed, Y=1),
                GcodeLinearMove(F=config.print_speed // 2, X=-60, E=e_raft),
                GcodeRapidMove(F=config.travel_speed, Y=1),
            ]
        )

    # Bring back to raft origin
    gcode.extend(
        [
            GcodeUseAbsolutePositioning(),
            GcodeRapidMove(
                F=config.travel_speed, X=xpos, Y=ypos, Z=config.layer_height * 3
            ),
            GcodeRapidMove(F=config.travel_speed, Z=config.layer_height * 2),
            GcodeUseIncrementalPositioning(),
        ]
    )

    # Vertical part of raft
    gcode.append(Comment("Layer 2"))
    for _ in range(30):
        gcode.extend(
            [
                GcodeLinearMove(F=config.print_speed // 2, Y=60, E=e_raft),
                GcodeRapidMove(F=config.travel_speed, X=1),
                GcodeLinearMove(F=config.print_speed // 2, Y=-60, E=e_raft),
                GcodeRapidMove(F=config.travel_speed, X=1),
            ]
        )

    # Bring back to Calibration Starting Position
    gcode.extend(
        [
            GcodeUseAbsolutePositioning(),
            GcodeRapidMove(
                F=config.travel_speed, X=xpos + 5, Y=ypos + 5, Z=config.layer_height * 3
            ),
            GcodeUseIncrementalPositioning(),
        ]
    )

    return gcode


def generate_retraction_calibration(config: GcodeConfig) -> list[TGcode]:
    """Get the full set of gcode for the retraction calibration test."""
    gcode: list[TGcode] = [line for line in generate_header(config)]

    # Print out starting gcode
    gcode.extend(start_gcode(config))

    # Write raft gcode to file
    gcode.extend(raft_gcode(config))

    # Relative Movements
    gcode.extend([Gcode("M83"), GcodeUseIncrementalPositioning()])

    # Tower
    for test_num in range(config.num_tests):
        gcode.extend(layer_group(config, test_num, 3))

    # Ending Gcode
    end_gcode = [
        GcodeLinearMove(Z=5),  # Raise 5mm
        GcodeUseAbsolutePositioning(),  # Absolute Position
        Gcode("G28", X=0, Y=0),  # Home X Y
        Gcode("M84"),  # Turn off Steppers
        Gcode("M107"),  # Turn off Fan
        Gcode("M104", S=0),  # Turn off Hotend
        Gcode("M140", S=0),  # Turn off Bed
    ]
    gcode.extend(end_gcode)

    return gcode
