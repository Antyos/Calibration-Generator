from .config import GcodeConfig
from .calibration_header import generate_header
from .calibration_tower import layer_group

def start_gcode(config) -> list[str]:
    """Gcode to start a print"""
    return [
        "; Start Gcode",
        f"M140 S{int(config.bed_temp)}",
        "M105",
        f"M190 S{int(config.bed_temp)}",
        f"M104 S{int(config.hotend_temp_init)}",
        "M105",
        f"M109 S{int(config.hotend_temp_init)}",
        "M82",
        "G28",
        "G92 E0",
        "G1 F200 E1",
        "G92 E0",
        f"{config.custom_gcode}",
        ";",
        ";",
    ]


def raft_gcode(config) -> list[str]:
    """Generate raft Gcode"""
    xpos = config.bed_shape_x / 2 - 30
    ypos = config.bed_shape_y / 2 - 30
    zpos = config.layer_height
    epos = 0

    gcode = [
        "; Start Movement",
        ";",
        "G1 Z2",
        f"G1 F{config.travel_speed} X{xpos} Y{ypos} Z{zpos}",
        ";",
    ]
    # Overextruding Raft
    e_raft = config.get_e_value(60)

    remx = xpos
    remy = ypos

    # Horizontal
    gcode.append("; Layer 1")
    for _ in range(30):
        epos += e_raft
        gcode.append(f"G1 F{config.print_speed//2} X{xpos+60} Y{ypos} E{epos:.5f}")
        xpos += 60
        epos += e_raft
        gcode.append(f"G0 F{config.travel_speed} X{xpos} Y{ypos+1}")
        ypos += 1
        gcode.append(f"G1 F{config.print_speed//2} X{xpos-60} Y{ypos} E{epos:.5f}")
        xpos -= 60
        epos += e_raft
        gcode.append(f"G0 F{config.travel_speed} X{xpos} Y{ypos+1}")
        ypos += 1

    # Bring back to raft origin
    gcode.append(
        f"G0 F{config.travel_speed} X{xpos} Y{ypos} Z{config.layer_height*3:.2f}"
    )
    gcode.append(
        f"G0 F{config.travel_speed} X{remx} Y{remy} Z{config.layer_height+config.layer_height}"
    )
    xpos = remx
    ypos = remy

    # Vertical
    gcode.append(";Layer 2")
    for _ in range(30):
        epos += e_raft
        gcode.append(f"G1 F{config.print_speed//2} X{xpos} Y{ypos+60} E{epos:.5f}")
        ypos += 60
        epos += e_raft
        gcode.append(f"G0 F{config.travel_speed} X{xpos+1} Y{ypos}")
        xpos += 1
        gcode.append(f"G1 F{config.print_speed//2} X{xpos} Y{ypos-60} E{epos:.5f}")
        ypos -= 60
        epos += e_raft
        gcode.append(f"G0 F{config.travel_speed} X{xpos+1} Y{ypos}")
        xpos += 1

    # Bring back to Calibration Starting Position
    gcode.append(
        f"G0 F{config.travel_speed} X{remx+5} Y{remy+5} Z{config.layer_height*3:.2f}"
    )

    return gcode



def generate_retraction_calibration(config: GcodeConfig) -> list[str]:
    """Get the full set of gcode for the retraction calibration test."""
    gcode = [f";{line}" for line in generate_header(config)]

    # Print out starting gcode
    gcode.extend(start_gcode(config))

    # Write raft gcode to file
    gcode.extend(raft_gcode(config))

    # Relative Movements
    gcode.extend(["M83", "G91"])

    # Tower
    for test_num in range(config.num_tests):
        gcode.extend(layer_group(config, test_num, 3))

    # Ending Gcode
    end_gcode = [
        "G1 Z5",  # Raise 5mm
        "G90",  # Absolute Position
        "G28 X0 Y0",  # Home X Y
        "M84",  # Turn off Steppers
        "M107",  # Turn off Fan
        "M104 S0",  # Turn off Hotend
        "M140 S0",  # Turn off Bed
    ]
    gcode.extend(end_gcode)

    return gcode
