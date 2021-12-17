from .config import GcodeConfig

def single_layer(config: GcodeConfig, big_section_num: int) -> list[str]:
    """Gcode for a single layer"""
    print_speed = config.print_speed
    travel_speed = config.travel_speed
    e_value = config.get_e_value(10)
    f_value = (
        config.retraction_speed_init
        + config.retraction_speed_delta * big_section_num * 60
    )
    dist_init = config.retraction_dist_init
    dist_delta = config.retraction_dist_delta

    gcode = []

    # Bottom
    for i in range(0 + 0, 4 + 0):
        gcode.extend(
            [
                f"G1 F{print_speed} X10 E{e_value:.5f}",
                f"G1 E{-(dist_init+dist_delta*i):.2f} F{f_value:.2f}",
                f"G0 F{travel_speed} Y-10",
                f"G0 F{travel_speed} Y10",
                f"G1 E{(dist_init+dist_delta*i):.2f} F{f_value:.2f}",
            ]
        )

    # Right
    for i in range(0 + 4, 4 + 4):
        gcode.extend(
            [
                f"G1 F{print_speed} Y10 E{e_value:.5f}",
                f"G1 E{-(dist_init+dist_delta*i):.2f} F{f_value:.2f}",
                f"G0 F{travel_speed} X10",
                f"G0 F{travel_speed} X-10",
                f"G1 E{(dist_init+dist_delta*i):.2f} F{f_value:.2f}",
            ]
        )

    # Top
    for i in range(0 + 8, 4 + 8):
        gcode.extend(
            [
                f"G1 F{print_speed} X-10 E{e_value:.5f}",
                f"G1 E{-(dist_init+dist_delta*i):.2f} F{f_value:.2f}",
                f"G0 F{travel_speed} Y10",
                f"G0 F{travel_speed} Y-10",
                f"G1 E{(dist_init+dist_delta*i):.2f} F{f_value:.2f}",
            ]
        )

    # Left
    for i in range(0 + 12, 4 + 12):
        gcode.extend(
            [
                f"G1 F{print_speed} Y-10 E{e_value:.5f}",
                f"G1 E{-(dist_init+dist_delta*i):.2f} F{f_value:.2f}",
                f"G0 F{travel_speed} X-10",
                f"G0 F{travel_speed} X10",
                f"G1 E{(dist_init+dist_delta*i):.2f} F{f_value:.2f}",
            ]
        )

    return gcode


def corner_marker(patterns: list[str], print_speed, e_speed) -> list[str]:
    return [f"G1 F{print_speed} {pattern} E{e_speed:.5f}" for pattern in patterns]


def layer_group(
    config: GcodeConfig, big_section_num: int, start_layer: int
) -> list[str]:
    """Generate a block of layers"""
    print_speed = config.print_speed
    travel_speed = config.travel_speed
    e_value = config.get_e_value(10)
    e_corner = config.get_e_value(1)
    f_value = (
        config.retraction_speed_init
        + config.retraction_speed_delta * big_section_num * 60
    )
    dist_init = config.retraction_dist_init
    dist_delta = config.retraction_dist_delta
    layer_height = config.layer_height

    layer_num = start_layer + big_section_num * config.layers_per_test

    gcode = [
        # Set Fan every 15 layers
        f"M106 S{(config.fan_speed_init+config.fan_speed_delta*big_section_num) * 255 / 100:d}",
        f"M104 S{config.hotend_temp_init+config.hotend_temp_change*big_section_num:d}",
        f";Layer {layer_num}",
    ]

    # Layer Marker Bottom Left
    gcode.extend(corner_marker(["X-2", "Y-2", "X2", "Y2"], print_speed, e_corner))

    # Bottom
    for i in range(0 + 0, 4 + 0):
        gcode.extend(
            [
                f"G1 F{print_speed} X10 E{e_value:.5f}",
                f"G1 E{-(dist_init+dist_delta*i):.2f} F{f_value:.2f}",
                f"G0 F{travel_speed} Y-10",
                f"G0 F{travel_speed} Y10",
                f"G1 E{(dist_init+dist_delta*i):.2f} F{f_value:.2f}",
            ]
        )

    # Layer Marker Bottom Right
    gcode.extend(corner_marker(["X1", "Y-1", "X-1", "Y1"], print_speed, e_corner))

    # Right
    for i in range(0 + 4, 4 + 4):
        gcode.extend(
            [
                f"G1 F{print_speed} Y10 E{e_value:.5f}",
                f"G1 E{-(dist_init+dist_delta*i):.2f} F{f_value:.2f}",
                f"G0 F{travel_speed} X10",
                f"G0 F{travel_speed} X-10",
                f"G1 E{(dist_init+dist_delta*i):.2f} F{f_value:.2f}",
            ]
        )

    # Layer Marker Top Right
    gcode.extend(corner_marker(["X1", "Y1", "X-1", "Y-1"], print_speed, e_corner))

    # Top
    for i in range(0 + 8, 4 + 8):
        gcode.extend(
            [
                f"G1 F{print_speed} X-10 E{e_value:.5f}",
                f"G1 E{-(dist_init+dist_delta*i):.2f} F{f_value:.2f}",
                f"G0 F{travel_speed} Y10",
                f"G0 F{travel_speed} Y-10",
                f"G1 E{(dist_init+dist_delta*i):.2f} F{f_value:.2f}",
            ]
        )

    # Layer Marker Top Left
    gcode.extend(corner_marker(["X-1", "Y1", "X1", "Y-1"], print_speed, e_corner))

    # Left
    for i in range(0 + 12, 4 + 12):
        gcode.extend(
            [
                f"G1 F{print_speed} Y-10 E{e_value:.5f}",
                f"G1 E{-(dist_init+dist_delta*i):.2f} F{f_value:.2f}",
                f"G0 F{travel_speed} X-10",
                f"G0 F{travel_speed} X10",
                f"G1 E{(dist_init+dist_delta*i):.2f} F{f_value:.2f}",
            ]
        )

    # Zup layer height
    gcode.append(f"G1 Z{layer_height}")

    # Do the rest of the layers without the loops
    for layer in range(config.layers_per_test - 1):
        gcode.append(f";Layer {layer_num+layer}")
        gcode.extend(single_layer(config, big_section_num))
        gcode.append(f"G1 Z{config.layer_height}")

    return gcode
