from euclid import Vector2
from retcal.gcode import Comment, Gcode, GcodeLinearMove, GcodeRapidMove, TGcode
from retcal.utils import vec_to_dict
from .config import GcodeConfig


def retraction_segment(
    vector: tuple[Vector2, Vector2],
    retraction_dist: float,
    retraction_flowrate: float,
    e_blob_dist: float,
    print_speed: float,
    travel_speed: float,
):
    """Line section"""
    return [
        GcodeLinearMove(**vec_to_dict(vector[0]), E=e_blob_dist, F=print_speed),
        GcodeLinearMove(E=-retraction_dist, F=retraction_flowrate),
        GcodeRapidMove(**vec_to_dict(vector[1]), F=travel_speed),
        GcodeRapidMove(**vec_to_dict(-vector[1]), F=travel_speed),
        GcodeLinearMove(E=retraction_dist, F=retraction_flowrate),
    ]


def single_layer(config: GcodeConfig, big_section_num: int) -> list[TGcode]:
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

    gcode: list[TGcode] = []

    # Bottom
    for i in range(0 + 0, 4 + 0):
        gcode.extend(
            retraction_segment(
                (Vector2(10, 0), Vector2(0, -10)),
                dist_init + dist_delta * i,
                f_value,
                e_value,
                print_speed,
                travel_speed,
            )
        )

    # Right
    for i in range(0 + 4, 4 + 4):
        gcode.extend(
            retraction_segment(
                (Vector2(0, 10), Vector2(10, 0)),
                dist_init + dist_delta * i,
                f_value,
                e_value,
                print_speed,
                travel_speed,
            )
        )

    # Top
    for i in range(0 + 8, 4 + 8):
        gcode.extend(
            retraction_segment(
                (Vector2(-10, 0), Vector2(0, 10)),
                dist_init + dist_delta * i,
                f_value,
                e_value,
                print_speed,
                travel_speed,
            )
        )

    # Left
    for i in range(0 + 12, 4 + 12):
        gcode.extend(
            retraction_segment(
                (Vector2(0, -10), Vector2(10, 0)),
                dist_init + dist_delta * i,
                f_value,
                e_value,
                print_speed,
                travel_speed,
            )
        )

    return gcode


def corner_marker(vectors: list[Vector2], print_speed, e_speed) -> list[TGcode]:
    return [
        GcodeLinearMove(**vec_to_dict(vec), E=e_speed, F=print_speed) for vec in vectors
    ]


def layer_group(
    config: GcodeConfig, big_section_num: int, start_layer: int
) -> list[TGcode]:
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

    gcode: list[TGcode] = [
        # Set Fan every 15 layers
        Gcode(
            "M106",
            S=(config.fan_speed_init + config.fan_speed_delta * big_section_num)
            * 255
            / 100,
        ),
        Gcode(
            "M104",
            S=config.hotend_temp_init + config.hotend_temp_change * big_section_num,
        ),
        Comment(f"Layer {layer_num}"),
    ]

    # Layer Marker Bottom Left
    gcode.extend(
        corner_marker(
            [
                Vector2(-2, 0),
                Vector2(0, -2),
                Vector2(2, 0),
                Vector2(0, 2),
            ],
            print_speed,
            e_corner,
        )
    )

    # Bottom
    for i in range(0 + 0, 4 + 0):
        gcode.extend(
            retraction_segment(
                (Vector2(10, 0), Vector2(0, -10)),
                dist_init + dist_delta * i,
                f_value,
                e_value,
                print_speed,
                travel_speed,
            )
        )

    # Layer Marker Bottom Right
    gcode.extend(
        corner_marker(
            [
                Vector2(1, 0),
                Vector2(0, -1),
                Vector2(-1, 0),
                Vector2(0, 1),
            ],
            print_speed,
            e_corner,
        )
    )

    # Right
    for i in range(0 + 4, 4 + 4):
        gcode.extend(
            retraction_segment(
                (Vector2(0, 10), Vector2(10, 0)),
                dist_init + dist_delta * i,
                f_value,
                e_value,
                print_speed,
                travel_speed,
            )
        )

    # Layer Marker Top Right
    gcode.extend(
        corner_marker(
            [
                Vector2(1, 0),
                Vector2(0, 1),
                Vector2(-1, 0),
                Vector2(0, -1),
            ],
            print_speed,
            e_corner,
        )
    )

    # Top
    for i in range(0 + 8, 4 + 8):
        gcode.extend(
            retraction_segment(
                (Vector2(-10, 0), Vector2(0, 10)),
                dist_init + dist_delta * i,
                f_value,
                e_value,
                print_speed,
                travel_speed,
            )
        )

    # Layer Marker Top Left
    gcode.extend(
        corner_marker(
            [
                Vector2(-1, 0),
                Vector2(0, 1),
                Vector2(1, 0),
                Vector2(0, -1),
            ],
            print_speed,
            e_corner,
        )
    )

    # Left
    for i in range(0 + 12, 4 + 12):
        gcode.extend(
            retraction_segment(
                (Vector2(0, -10), Vector2(10, 0)),
                dist_init + dist_delta * i,
                f_value,
                e_value,
                print_speed,
                travel_speed,
            )
        )

    # Zup layer height
    gcode.append(GcodeLinearMove(Z=layer_height))

    # Do the rest of the layers without the loops
    for layer in range(config.layers_per_test - 1):
        gcode.append(Comment(f"Layer {layer_num+layer}"))
        gcode.extend(single_layer(config, big_section_num))
        gcode.append(GcodeLinearMove(Z=config.layer_height))

    return gcode
