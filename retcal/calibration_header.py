from dataclasses import asdict
from retcal.config import GcodeConfig
from retcal.gcode import Comment

def retraction_distance_diagram(start_distance: float, increment: float) -> list[str]:
    """Create a top-down diagram of the retraction distances."""
    retraction_dists = [start_distance + increment * i for i in range(16)]

    return [
        "Retraction Distance from the top looking down",
        "",
        # Add top row of numbers
        f"{'':10}"
        + "  ".join(f"{dist:<6.2f}" for dist in retraction_dists[11 : 8 - 1 : -1]),
        # Print top row of bars
        f"{'':10}" + f"{'|':8}" * 4,
        # Side rows
        f"{retraction_dists[12]:6.2f} -  {'':32}- {retraction_dists[7]:<6.2f}",
        "",
        "",
        f"{retraction_dists[13]:6.2f} -  {'':32}- {retraction_dists[6]:<6.2f}",
        "",
        "",
        f"{retraction_dists[14]:6.2f} -  {'':32}- {retraction_dists[5]:<6.2f}",
        "",
        "",
        f"{retraction_dists[15]:6.2f} -  {'':32}- {retraction_dists[4]:<6.2f}",
        "",
        # Print bottom row of bars
        f"{'':10}" + f"{'|':8}" * 4,
        # Print bottom for of numbers
        f"{'':10}" + "  ".join(f"{dist:<6.2f}" for dist in retraction_dists[:4]),
    ]


def variables_by_height(config: GcodeConfig) -> list[str]:
    """Get a string containing variables listed by height"""
    # Header
    _str = [
        "Variables by Height",
        "",
        f"{'Num':15}{'Retraction':12}{'Nozzle':12}{'Fan':12}",
        f"{'Layers':15}{'Speed':12}{'Temp':12}{'Speed':12}",
        "",
    ]

    # Rows
    for test in range(config.num_tests):
        _str.append(
            f"{config.layers_per_test:15}{config.retraction_speed_init+config.retraction_speed_delta*test:12.2}"
            + f"{config.hotend_temp_init+config.hotend_temp_change*test:12.2}{config.fan_speed_init+config.fan_speed_delta*test:12.2}"
        )

    # Strip trailing spaces and return
    return [s.strip() for s in _str]


def generate_header(config: GcodeConfig) -> list[Comment]:
    """Generate the retraction calibration header."""
    title_str = "Calibration Generator 1.3.3"
    header = [
        title_str,
        "",
        "",
    ]

    # Retraction distance diagram
    header.extend(
        retraction_distance_diagram(
            config.retraction_dist_init, config.retraction_dist_delta
        )
    )
    header.extend(["", ""])

    # Print variables by height
    header.extend(variables_by_height(config))
    header.extend(["", ""])

    # Print variables
    header.extend([" All inputs", ""])
    header.extend([f"{key} = {value}" for key, value in asdict(config).values()])
    header.extend(["", ""])

    return [Comment(line) for line in header]
