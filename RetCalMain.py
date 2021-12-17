# -*- coding: utf-8 -*-

from dataclasses import asdict, dataclass

from PyQt5 import QtCore, QtGui, QtWidgets
from RetCalui import Ui_MainWindow
from decimal import Decimal

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
        area = (self.nozzle_diameter - self.layer_height) * self.layer_height + 3.14159 * (self.layer_height/2)**2
        return (area * extrusion_length * 4)/(3.14159 * self.dilament_diameter **2/ self.extrusion_multiplier)

def retraction_distance_diagram(
    start_distance: float, increment: float
) -> list[str]:
    """Create a top-down diagram of the retraction distances."""
    retraction_dists = [round(Decimal(start_distance + increment * i), 2) for i in range(16)]

    return [
        "Retraction Distance from the top looking down",
        "",
        # Add top row of numbers
        " "*10 + "  ".join(f"{dist:<6.2f}" for dist in retraction_dists[11 : 8-1 : -1]),
        # Print top row of bars
        " "*10 + f"{'|':8}"*4,
        # Side rows
        f"{retraction_dists[12]:6.2f} -  " + " "*32 +f"- {retraction_dists[7]:<6.2f}",
        "",
        "",
        f"{retraction_dists[13]:6.2f} -  " + " "*32 +f"- {retraction_dists[6]:<6.2f}",
        "",
        "",
        f"{retraction_dists[14]:6.2f} -  " + " "*32 +f"- {retraction_dists[5]:<6.2f}",
        "",
        "",
        f"{retraction_dists[15]:6.2f} -  " + " "*32 +f"- {retraction_dists[4]:<6.2f}",
        "",
        # Print bottom row of bars
        " "*10 + f"{'|':8}"*4,
        # Print bottom for of numbers
        " "*10 + "  ".join(f"{dist:<6.2f}" for dist in retraction_dists[:4]),
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

def start_gcode(config) -> list[str]:
    """Gcode to start a print """
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
    xpos = config.bed_shape_x/2-30
    ypos = config.bed_shape_y/2-30
    zpos = config.layer_height
    epos = 0

    gcode = [
        "; Start Movement",
        ";",
        "G1 Z2",
        f"G1 F{config.travel_speed} X{xpos} Y{ypos} Z{zpos}",
        ";",
    ]
    #Overextruding Raft
    e_raft = config.get_e_value(60)

    remx = xpos
    remy = ypos


    #Horizontal
    gcode.append('; Layer 1')
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

    #Bring back to raft origin
    gcode.append(f"G0 F{config.travel_speed} X{xpos} Y{ypos} Z{config.layer_height*3:.2f}")
    gcode.append(f"G0 F{config.travel_speed} X{remx} Y{remy} Z{config.layer_height+config.layer_height}")
    xpos = remx
    ypos = remy

    #Vertical
    gcode.append(';Layer 2')
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

    #Bring back to Calibration Starting Position
    gcode.append(f"G0 F{config.travel_speed} X{remx+5} Y{remy+5} Z{config.layer_height*3:.2f}")

    return gcode

def single_layer(config: GcodeConfig, big_section_num: int) -> list[str]:
    """Gcode for a single layer"""
    print_speed = config.print_speed
    travel_speed = config.travel_speed
    e_value = config.get_e_value(10)
    f_value = config.retraction_speed_init + config.retraction_speed_delta * big_section_num * 60
    dist_init = config.retraction_dist_init
    dist_delta = config.retraction_dist_delta

    gcode = []

    #Bottom
    for i in range(0+0, 4+0):
        gcode.extend([
            f"G1 F{print_speed} X10 E{e_value:.5f}",
            f"G1 E{-(dist_init+dist_delta*i):.2f} F{f_value:.2f}",
            f"G0 F{travel_speed} Y-10",
            f"G0 F{travel_speed} Y10",
            f"G1 E{(dist_init+dist_delta*i):.2f} F{f_value:.2f}",
        ])

    #Right
    for i in range(0+4, 4+4):
        gcode.extend([
            f"G1 F{print_speed} Y10 E{e_value:.5f}",
            f"G1 E{-(dist_init+dist_delta*i):.2f} F{f_value:.2f}",
            f"G0 F{travel_speed} X10",
            f"G0 F{travel_speed} X-10",
            f"G1 E{(dist_init+dist_delta*i):.2f} F{f_value:.2f}",
        ])

    #Top
    for i in range(0+8, 4+8):
        gcode.extend([
            f"G1 F{print_speed} X-10 E{e_value:.5f}",
            f"G1 E{-(dist_init+dist_delta*i):.2f} F{f_value:.2f}",
            f"G0 F{travel_speed} Y10",
            f"G0 F{travel_speed} Y-10",
            f"G1 E{(dist_init+dist_delta*i):.2f} F{f_value:.2f}",
        ])

    #Left
    for i in range(0+12, 4+12):
        gcode.extend([
            f"G1 F{print_speed} Y-10 E{e_value:.5f}",
            f"G1 E{-(dist_init+dist_delta*i):.2f} F{f_value:.2f}",
            f"G0 F{travel_speed} X-10",
            f"G0 F{travel_speed} X10",
            f"G1 E{(dist_init+dist_delta*i):.2f} F{f_value:.2f}",
        ])

    return gcode

def button_clicked(ui: Ui_MainWindow):
    name = QtWidgets.QFileDialog.getSaveFileName(
        ui.centralwidget,
        'Save Gcode',
        filter="(*.gcode)"
    )
    
    # Return if no file name
    if len(name[0]) == 0:
        return
        
    file = open(name[0],'w')

    cfg = GcodeConfig(
        # Start Gcode Retraction Distance
        retraction_dist_init=float(ui.startRetractiondistance.text()),
        retraction_dist_delta=float(ui.incrementRetractiondistance.text()),
        #Variables by Height
        retraction_speed_init=float(ui.startRetractionspeed.text()),
        retraction_speed_delta=float(ui.incrementRetractionspeed.text()),
        hotend_temp_init=float(ui.tempStarthotend.text()),
        hotend_temp_change=float(ui.tempIncrementhotend.text()),
        fan_speed_init=int(ui.speedFan.text()),
        fan_speed_delta=int(ui.speedFanIncrement.text()),
        layer_height=float(ui.layerHeight.text()),
        layers_per_test=int(ui.layersTest.text()),
        num_tests=int(ui.NumTests.text()),
        # Printer parameters
        bed_shape_x=float(ui.dimensionX.text()),
        bed_shape_y=float(ui.dimensionY.text()),
        print_speed=int(ui.printSpeed.text()) * 60,
        travel_speed=int(ui.speedTravel.text()) * 60,
        nozzle_diameter=float(ui.nozzleDiameter.text()),
        dilament_diameter=float(ui.filamentDiameter.text()),
        extrusion_multiplier=float(ui.extrusionMultiplier.text()),
        bed_temp=float(ui.tempBed.text()),
        # Custom Gcode
        custom_gcode=str(ui.customGcode.toPlainText()),
    )
    
    # Array of retraction distances
    
    title_str = "Calibration Generator 1.3.3"
    file.write(f";{title_str}\n")
    file.write(f";\n;\n")

    # Print retraction distance diagram
    diagram_str = retraction_distance_diagram(cfg.retraction_dist_init, cfg.retraction_dist_delta)
    for s in diagram_str:
        file.write(f";{s}\n")
    file.write(f";\n;\n")

    # Print variables by height
    for s in variables_by_height(cfg):
        file.write(f";{s}\n")

    # Print variables
    file.write(f";\n;\n")
    file.write(f"; All inputs\n")
    file.write(f";\n")
    for key, value in asdict(cfg).values():
        file.write(f";{key} = {value}\n")
    file.write(f";\n;\n")

    # Print out starting gcode
    file.write("\n".join(start_gcode(cfg)) + "\n")
    
    # Write raft gcode to file
    file.write("\n".join(raft_gcode(cfg)) + "\n")

    #Relative Movements

    file.write(f"M83\n")
    file.write(f"G91\n")

    #Start Calibration

    eValueresult = cfg.get_e_value(10)
    corenermarker = cfg.get_e_value(1)

    loopbigcount = 0
    loopsmallcount = 0

    layer = 3

    cnt = int(cfg.num_tests)
    cfg.layers_per_test -= 1

    for loopbig in range(int(cnt)):

    # Set Fan every 15 layers
        file.write(f"M106 S{(round(Decimal((cfg.fan_speed_init+cfg.fan_speed_delta*loopbigcount)) * 255 / 100,0))  }\n")
        file.write(f"M104 S{round(Decimal(cfg.hotend_temp_init+cfg.hotend_temp_change*loopbigcount),0)}\n")

        file.write(f";Layer {layer}\n")

        #Layer Marker Bottom Left
        file.write(f"G1 F{cfg.print_speed} X-2 E{round(Decimal(corenermarker),5)}\n")
        file.write(f"G1 F{cfg.print_speed} Y-2 E{round(Decimal(corenermarker),5)}\n")
        file.write(f"G1 F{cfg.print_speed} X2 E{round(Decimal(corenermarker),5)}\n")
        file.write(f"G1 F{cfg.print_speed} Y2 E{round(Decimal(corenermarker),5)}\n")


        #Begin

        #Bottom
        file.write(f"G1 F{cfg.print_speed} X10 E{round(Decimal(eValueresult),5)}\n")
        file.write(f"G1 E{round(Decimal(cfg.retraction_dist_init+cfg.retraction_dist_delta*0),2) * -1} F{round(Decimal((cfg.retraction_speed_init+cfg.retraction_speed_delta*loopbigcount) * 60),2)}\n")
        file.write(f"G0 F{cfg.travel_speed} Y-10\n")
        file.write(f"G0 F{cfg.travel_speed} Y10\n")
        file.write(f"G1 E{round(Decimal(cfg.retraction_dist_init+cfg.retraction_dist_delta*0),2)} F{round(Decimal((cfg.retraction_speed_init+cfg.retraction_speed_delta*loopbigcount) * 60),2)}\n")
        file.write(f"G1 F{cfg.print_speed} X10 E{round(Decimal(eValueresult),5)}\n")
        file.write(f"G1 E{round(Decimal(cfg.retraction_dist_init+cfg.retraction_dist_delta*1),2) * -1} F{round(Decimal((cfg.retraction_speed_init+cfg.retraction_speed_delta*loopbigcount) * 60),2)}\n")
        file.write(f"G0 F{cfg.travel_speed} Y-10\n")
        file.write(f"G0 F{cfg.travel_speed} Y10\n")
        file.write(f"G1 E{round(Decimal(cfg.retraction_dist_init+cfg.retraction_dist_delta*1),2)} F{round(Decimal((cfg.retraction_speed_init+cfg.retraction_speed_delta*loopbigcount) * 60),2)}\n")
        file.write(f"G1 F{cfg.print_speed} X10 E{round(Decimal(eValueresult),5)}\n")
        file.write(f"G1 E{round(Decimal(cfg.retraction_dist_init+cfg.retraction_dist_delta*2),2) * -1} F{round(Decimal((cfg.retraction_speed_init+cfg.retraction_speed_delta*loopbigcount) * 60),2)}\n")
        file.write(f"G0 F{cfg.travel_speed} Y-10\n")
        file.write(f"G0 F{cfg.travel_speed} Y10\n")
        file.write(f"G1 E{round(Decimal(cfg.retraction_dist_init+cfg.retraction_dist_delta*2),2)} F{round(Decimal((cfg.retraction_speed_init+cfg.retraction_speed_delta*loopbigcount) * 60),2)}\n")
        file.write(f"G1 F{cfg.print_speed} X10 E{round(Decimal(eValueresult),5)}\n")
        file.write(f"G1 E{round(Decimal(cfg.retraction_dist_init+cfg.retraction_dist_delta*3),2) * -1} F{round(Decimal((cfg.retraction_speed_init+cfg.retraction_speed_delta*loopbigcount) * 60),2)}\n")
        file.write(f"G0 F{cfg.travel_speed} Y-10\n")
        file.write(f"G0 F{cfg.travel_speed} Y10\n")
        file.write(f"G1 E{round(Decimal(cfg.retraction_dist_init+cfg.retraction_dist_delta*3),2)} F{round(Decimal((cfg.retraction_speed_init+cfg.retraction_speed_delta*loopbigcount) * 60),2)}\n")
        file.write(f"G1 F{cfg.print_speed} X10 E{round(Decimal(eValueresult),5)}\n")

        #Layer Marker Bottom Right
        file.write(f"G1 F{cfg.print_speed} X1 E{round(Decimal(corenermarker),5)}\n")
        file.write(f"G1 F{cfg.print_speed} Y-1 E{round(Decimal(corenermarker),5)}\n")
        file.write(f"G1 F{cfg.print_speed} X-1 E{round(Decimal(corenermarker),5)}\n")
        file.write(f"G1 F{cfg.print_speed} Y1 E{round(Decimal(corenermarker),5)}\n")

        #Right
        file.write(f"G1 F{cfg.print_speed} Y10 E{round(Decimal(eValueresult),5)}\n")
        file.write(f"G1 E{round(Decimal(cfg.retraction_dist_init+cfg.retraction_dist_delta*4),2) * -1} F{round(Decimal((cfg.retraction_speed_init+cfg.retraction_speed_delta*loopbigcount) * 60),2)}\n")
        file.write(f"G0 F{cfg.travel_speed} X10\n")
        file.write(f"G0 F{cfg.travel_speed} X-10\n")
        file.write(f"G1 E{round(Decimal(cfg.retraction_dist_init+cfg.retraction_dist_delta*4),2)} F{round(Decimal((cfg.retraction_speed_init+cfg.retraction_speed_delta*loopbigcount) * 60),2)}\n")
        file.write(f"G1 F{cfg.print_speed} Y10 E{round(Decimal(eValueresult),5)}\n")
        file.write(f"G1 E{round(Decimal(cfg.retraction_dist_init+cfg.retraction_dist_delta*5),2) * -1} F{round(Decimal((cfg.retraction_speed_init+cfg.retraction_speed_delta*loopbigcount) * 60),2)}\n")
        file.write(f"G0 F{cfg.travel_speed} X10\n")
        file.write(f"G0 F{cfg.travel_speed} X-10\n")
        file.write(f"G1 E{round(Decimal(cfg.retraction_dist_init+cfg.retraction_dist_delta*5),2)} F{round(Decimal((cfg.retraction_speed_init+cfg.retraction_speed_delta*loopbigcount) * 60),2)}\n")
        file.write(f"G1 F{cfg.print_speed} Y10 E{round(Decimal(eValueresult),5)}\n")
        file.write(f"G1 E{round(Decimal(cfg.retraction_dist_init+cfg.retraction_dist_delta*6),2) * -1} F{round(Decimal((cfg.retraction_speed_init+cfg.retraction_speed_delta*loopbigcount) * 60),2)}\n")
        file.write(f"G0 F{cfg.travel_speed} X10\n")
        file.write(f"G0 F{cfg.travel_speed} X-10\n")
        file.write(f"G1 E{round(Decimal(cfg.retraction_dist_init+cfg.retraction_dist_delta*6),2)} F{round(Decimal((cfg.retraction_speed_init+cfg.retraction_speed_delta*loopbigcount) * 60),2)}\n")
        file.write(f"G1 F{cfg.print_speed} Y10 E{round(Decimal(eValueresult),5)}\n")
        file.write(f"G1 E{round(Decimal(cfg.retraction_dist_init+cfg.retraction_dist_delta*7),2) * -1} F{round(Decimal((cfg.retraction_speed_init+cfg.retraction_speed_delta*loopbigcount) * 60),2)}\n")
        file.write(f"G0 F{cfg.travel_speed} X10\n")
        file.write(f"G0 F{cfg.travel_speed} X-10\n")
        file.write(f"G1 E{round(Decimal(cfg.retraction_dist_init+cfg.retraction_dist_delta*7),2)} F{round(Decimal((cfg.retraction_speed_init+cfg.retraction_speed_delta*loopbigcount) * 60),2)}\n")
        file.write(f"G1 F{cfg.print_speed} Y10 E{round(Decimal(eValueresult),5)}\n")

        #Layer Marker Top Right
        file.write(f"G1 F{cfg.print_speed} X1 E{round(Decimal(corenermarker),5)}\n")
        file.write(f"G1 F{cfg.print_speed} Y1 E{round(Decimal(corenermarker),5)}\n")
        file.write(f"G1 F{cfg.print_speed} X-1 E{round(Decimal(corenermarker),5)}\n")
        file.write(f"G1 F{cfg.print_speed} Y-1 E{round(Decimal(corenermarker),5)}\n")

        #Top
        file.write(f"G1 F{cfg.print_speed} X-10 E{round(Decimal(eValueresult),5)}\n")
        file.write(f"G1 E{round(Decimal(cfg.retraction_dist_init+cfg.retraction_dist_delta*8),2) * -1} F{round(Decimal((cfg.retraction_speed_init+cfg.retraction_speed_delta*loopbigcount) * 60),2)}\n")
        file.write(f"G0 F{cfg.travel_speed} Y10\n")
        file.write(f"G0 F{cfg.travel_speed} Y-10\n")
        file.write(f"G1 E{round(Decimal(cfg.retraction_dist_init+cfg.retraction_dist_delta*8),2)} F{round(Decimal((cfg.retraction_speed_init+cfg.retraction_speed_delta*loopbigcount) * 60),2)}\n")
        file.write(f"G1 F{cfg.print_speed} X-10 E{round(Decimal(eValueresult),5)}\n")
        file.write(f"G1 E{round(Decimal(cfg.retraction_dist_init+cfg.retraction_dist_delta*9),2) * -1} F{round(Decimal((cfg.retraction_speed_init+cfg.retraction_speed_delta*loopbigcount) * 60),2)}\n")
        file.write(f"G0 F{cfg.travel_speed} Y10\n")
        file.write(f"G0 F{cfg.travel_speed} Y-10\n")
        file.write(f"G1 E{round(Decimal(cfg.retraction_dist_init+cfg.retraction_dist_delta*9),2)} F{round(Decimal((cfg.retraction_speed_init+cfg.retraction_speed_delta*loopbigcount) * 60),2)}\n")
        file.write(f"G1 F{cfg.print_speed} X-10 E{round(Decimal(eValueresult),5)}\n")
        file.write(f"G1 E{round(Decimal(cfg.retraction_dist_init+cfg.retraction_dist_delta*10),2) * -1} F{round(Decimal((cfg.retraction_speed_init+cfg.retraction_speed_delta*loopbigcount) * 60),2)}\n")
        file.write(f"G0 F{cfg.travel_speed} Y10\n")
        file.write(f"G0 F{cfg.travel_speed} Y-10\n")
        file.write(f"G1 E{round(Decimal(cfg.retraction_dist_init+cfg.retraction_dist_delta*10),2)} F{round(Decimal((cfg.retraction_speed_init+cfg.retraction_speed_delta*loopbigcount) * 60),2)}\n")
        file.write(f"G1 F{cfg.print_speed} X-10 E{round(Decimal(eValueresult),5)}\n")
        file.write(f"G1 E{round(Decimal(cfg.retraction_dist_init+cfg.retraction_dist_delta*11),2) * -1} F{round(Decimal((cfg.retraction_speed_init+cfg.retraction_speed_delta*loopbigcount) * 60),2)}\n")
        file.write(f"G0 F{cfg.travel_speed} Y10\n")
        file.write(f"G0 F{cfg.travel_speed} Y-10\n")
        file.write(f"G1 E{round(Decimal(cfg.retraction_dist_init+cfg.retraction_dist_delta*11),2)} F{round(Decimal((cfg.retraction_speed_init+cfg.retraction_speed_delta*loopbigcount) * 60),2)}\n")
        file.write(f"G1 F{cfg.print_speed} X-10 E{round(Decimal(eValueresult),5)}\n")

        #Layer Marker Top Left
        file.write(f"G1 F{cfg.print_speed} X-1 E{round(Decimal(corenermarker),5)}\n")
        file.write(f"G1 F{cfg.print_speed} Y1 E{round(Decimal(corenermarker),5)}\n")
        file.write(f"G1 F{cfg.print_speed} X1 E{round(Decimal(corenermarker),5)}\n")
        file.write(f"G1 F{cfg.print_speed} Y-1 E{round(Decimal(corenermarker),5)}\n")

        #Left
        file.write(f"G1 F{cfg.print_speed} Y-10 E{round(Decimal(eValueresult),5)}\n")
        file.write(f"G1 E{round(Decimal(cfg.retraction_dist_init+cfg.retraction_dist_delta*12),2) * -1} F{round(Decimal((cfg.retraction_speed_init+cfg.retraction_speed_delta*loopbigcount) * 60),2)}\n")
        file.write(f"G0 F{cfg.travel_speed} X-10\n")
        file.write(f"G0 F{cfg.travel_speed} X10\n")
        file.write(f"G1 E{round(Decimal(cfg.retraction_dist_init+cfg.retraction_dist_delta*12),2)} F{round(Decimal((cfg.retraction_speed_init+cfg.retraction_speed_delta*loopbigcount) * 60),2)}\n")
        file.write(f"G1 F{cfg.print_speed} Y-10 E{round(Decimal(eValueresult),5)}\n")
        file.write(f"G1 E{round(Decimal(cfg.retraction_dist_init+cfg.retraction_dist_delta*13),2) * -1} F{round(Decimal((cfg.retraction_speed_init+cfg.retraction_speed_delta*loopbigcount) * 60),2)}\n")
        file.write(f"G0 F{cfg.travel_speed} X-10\n")
        file.write(f"G0 F{cfg.travel_speed} X10\n")
        file.write(f"G1 E{round(Decimal(cfg.retraction_dist_init+cfg.retraction_dist_delta*13),2)} F{round(Decimal((cfg.retraction_speed_init+cfg.retraction_speed_delta*loopbigcount) * 60),2)}\n")
        file.write(f"G1 F{cfg.print_speed} Y-10 E{round(Decimal(eValueresult),5)}\n")
        file.write(f"G1 E{round(Decimal(cfg.retraction_dist_init+cfg.retraction_dist_delta*14),2) * -1} F{round(Decimal((cfg.retraction_speed_init+cfg.retraction_speed_delta*loopbigcount) * 60),2)}\n")
        file.write(f"G0 F{cfg.travel_speed} X-10\n")
        file.write(f"G0 F{cfg.travel_speed} X10\n")
        file.write(f"G1 E{round(Decimal(cfg.retraction_dist_init+cfg.retraction_dist_delta*14),2)} F{round(Decimal((cfg.retraction_speed_init+cfg.retraction_speed_delta*loopbigcount) * 60),2)}\n")
        file.write(f"G1 F{cfg.print_speed} Y-10 E{round(Decimal(eValueresult),5)}\n")
        file.write(f"G1 E{round(Decimal(cfg.retraction_dist_init+cfg.retraction_dist_delta*15),2) * -1} F{round(Decimal((cfg.retraction_speed_init+cfg.retraction_speed_delta*loopbigcount) * 60),2)}\n")
        file.write(f"G0 F{cfg.travel_speed} X-10\n")
        file.write(f"G0 F{cfg.travel_speed} X10\n")
        file.write(f"G1 E{round(Decimal(cfg.retraction_dist_init+cfg.retraction_dist_delta*15),2)} F{round(Decimal((cfg.retraction_speed_init+cfg.retraction_speed_delta*loopbigcount) * 60),2)}\n")
        file.write(f"G1 F{cfg.print_speed} Y-10 E{round(Decimal(eValueresult),5)}\n")

        #Zup layer height

        file.write(f"G1 Z{cfg.layer_height}\n")
             
        # loopbigcount = loopbigcount +1
        layer += 1


        for _ in range(cfg.layers_per_test):
            file.write(f";Layer {layer}\n")
            file.write("\n".join(single_layer(cfg, loopbigcount)))
            file.write(f"G1 Z{cfg.layer_height}")
            layer += 1

        loopbigcount = loopbigcount +1


    # Ending Gcode
    end_gcode = [
        "G1 Z5",  #Raise 5mm
        "G90",  # Absolute Position
        "G28 X0 Y0",  # Home X Y
        "M84",  # Turn off Steppers
        "M107",  # Turn off Fan
        "M104 S0",  # Turn off Hotend
        "M140 S0",  #Turn off Bed
    ]
    file.write("\n".join(end_gcode))

    file.close()

def main():
    import sys
    
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    def _button_clicked():
        """Wrapper for gen_gcode()"""
        return button_clicked(ui)

    ui.genGcode.clicked.connect(_button_clicked)
    MainWindow.show()
    
    sys.exit(app.exec_())



if __name__ == "__main__":
    main()
    