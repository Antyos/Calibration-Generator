from dataclasses import dataclass

@dataclass
class GcodeConfig:
    retraction_dist_init: float
    retraction_dist_delta: float
    retraction_speed_init: float
    retraction_speed_delta: float
    hotend_temp_init: float
    hotend_temp_change: float
    fan_speed_init: int
    fan_speed_delta: int
    layer_height: float
    layers_per_test: int
    num_tests: int
    bed_shape_x: float
    bed_shape_y: float
    print_speed: int
    travel_speed: int
    nozzle_diameter: float
    dilament_diameter: float
    extrusion_multiplier: float
    bed_temp: float
    custom_gcode: str

    def get_e_value(self, extrusion_length):
        """Generate an E value for an extrusion length.

        See Also
        --------
        https://3dprinting.stackexchange.com/questions/10171/how-is-e-value-calculated-in-slic3r
        """
        area = (
            self.nozzle_diameter - self.layer_height
        ) * self.layer_height + 3.14159 * (self.layer_height / 2) ** 2
        return (area * extrusion_length * 4) / (
            3.14159 * self.dilament_diameter ** 2 / self.extrusion_multiplier
        )
