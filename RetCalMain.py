# -*- coding: utf-8 -*-

from dataclasses import asdict, dataclass

from PyQt5 import QtCore, QtGui, QtWidgets
from RetCalui import Ui_MainWindow
from decimal import Decimal

@dataclass
class GcodeConfig:
    srd: float
    ird: float
    srs: float
    irs: float
    tsh: float
    tih: float
    fs: float
    fsi: float
    lh: float
    ts: float
    lt: int
    nt: int
    dx: float
    dy: float
    ps: float
    nd: float
    fd: float
    em: float
    tb: float
    sgcode: str

    def get_e_value(self, extrusion_length):
        """Generate an E value for an extrusion length.
        
        See Also
        --------
        https://3dprinting.stackexchange.com/questions/10171/how-is-e-value-calculated-in-slic3r
        """
        area = (self.nd - self.lh) * self.lh + 3.14159 * (self.lh/2)**2
        return (area * extrusion_length * 4)/(3.14159 * self.fd **2/ self.em)

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
    for test in range(config.nt):
        _str.append(
            f"{config.lt:15}{config.srs+config.irs*test:12.2}"
            + f"{config.tsh+config.tih*test:12.2}{config.fs+config.fsi*test:12.2}"
        )

    # Strip trailing spaces and return
    return [s.strip() for s in _str]

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
        srd = float(ui.startRetractiondistance.text()),
        ird = float(ui.incrementRetractiondistance.text()),
        #Variables by Height
        srs = float(ui.startRetractionspeed.text()),
        irs = float(ui.incrementRetractionspeed.text()),
        tsh = float(ui.tempStarthotend.text()),
        tih = float(ui.tempIncrementhotend.text()),
        fs = float(ui.speedFan.text()),
        fsi = float(ui.speedFanIncrement.text()),
        lh = float(ui.layerHeight.text()),
        ts = float(ui.speedTravel.text()),
        lt = int(ui.layersTest.text()),
        nt = int(ui.NumTests.text()),
        # Printer parameters
        dx = float(ui.dimensionX.text()),
        dy = float(ui.dimensionY.text()),
        ps = float(ui.printSpeed.text()),
        nd = float(ui.nozzleDiameter.text()),
        fd = float(ui.filamentDiameter.text()),
        em = float(ui.extrusionMultiplier.text()),
        tb = float(ui.tempBed.text()),
        # Custom Gcode
        sgcode = str(ui.customGcode.toPlainText()),
    )
    
    # Array of retraction distances
    
    title_str = "Calibration Generator 1.3.3"
    file.write(f";{title_str}\n")
    file.write(f";\n;\n")

    # Print retraction distance diagram
    diagram_str = retraction_distance_diagram(cfg.srd, cfg.ird)
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

    #start Gcode
    file.write(f";Start Gcode\n")
    file.write(f"M140 S{int(cfg.tb)}\n")
    file.write(f"M105\n")
    file.write(f"M190 S{int(cfg.tb)}\n")
    file.write(f"M104 S{int(cfg.tsh)}\n")
    file.write(f"M105\n")
    file.write(f"M109 S{int(cfg.tsh)}\n")
    file.write(f"M82\n")
    file.write(f"G28\n")
    file.write(f"G92 E0\n")
    file.write(f"G1 F200 E1\n")
    file.write(f"G92 E0\n")
    file.write(f"{cfg.sgcode}\n")
    file.write(f";\n")
    file.write(f";\n")

    xpos = cfg.dx/2-30
    ypos = cfg.dy/2-30
    zpos = cfg.lh
    epos = 0

    #Start Movement
    file.write(f";Start Movement\n")
    file.write(f";\n")
    file.write(f"G1 Z2\n")
    file.write(f"G1 F{int(cfg.ts)*60} X{xpos} Y{ypos} Z{zpos}\n")
    file.write(f";\n")
    eValueresult = cfg.get_e_value(60)

    #Overextruding Raft
    evalueincrease = eValueresult*1.25
    eValueresult = evalueincrease


    remx = xpos
    remy = ypos

    file.write(f";Layer 1\n")

    #Horizontal

    for loopx in range(30):
        file.write(f"G1 F{int(cfg.ps*60/2)} X{xpos+60} Y{ypos} E{round(Decimal(eValueresult),5)}\n")
        xpos = xpos + 60
        eValueresult = eValueresult + evalueincrease
        file.write(f"G0 F{int(cfg.ts)*60} X{xpos} Y{ypos+1}\n")
        ypos = ypos + 1
        file.write(f"G1 F{int(cfg.ps*60/2)} X{xpos-60} Y{ypos} E{round(Decimal(eValueresult),5)}\n")
        xpos = xpos - 60
        eValueresult = eValueresult + evalueincrease
        file.write(f"G0 F{int(cfg.ts)*60} X{xpos} Y{ypos+1}\n")
        ypos = ypos + 1

    #Bring back to raft origin

    file.write(f"G0 F{int(cfg.ts)*60} X{xpos} Y{ypos} Z{round(Decimal(cfg.lh*3),2)}\n")
    file.write(f"G0 F{int(cfg.ts)*60} X{remx} Y{remy} Z{cfg.lh+cfg.lh}\n")
    xpos = remx
    ypos = remy

    file.write(f";Layer 2\n")

    #Vertical

    for loopx in range(30):
        file.write(f"G1 F{int(cfg.ps*60/2)} X{xpos} Y{ypos+60} E{round(Decimal(eValueresult),5)}\n")
        ypos = ypos + 60
        eValueresult = eValueresult + evalueincrease
        file.write(f"G0 F{int(cfg.ts)*60} X{xpos+1} Y{ypos}\n")
        xpos = xpos + 1
        file.write(f"G1 F{int(cfg.ps*60/2)} X{xpos} Y{ypos-60} E{round(Decimal(eValueresult),5)}\n")
        ypos = ypos - 60
        eValueresult = eValueresult + evalueincrease
        file.write(f"G0 F{int(cfg.ts)*60} X{xpos+1} Y{ypos}\n")
        xpos = xpos + 1

    #Bring back to Calibration Starting Position

    file.write(f"G0 F{int(cfg.ts)*60} X{remx+5} Y{remy+5} Z{round(Decimal(cfg.lh*3),2)}\n")

    #Relative Movements

    file.write(f"M83\n")
    file.write(f"G91\n")

    #Start Calibration

    eValueresult = cfg.get_e_value(10)
    corenermarker = cfg.get_e_value(1)

    loopbigcount = 0
    loopsmallcount = 0

    layer = 3

    cnt = int(cfg.nt)
    cfg.lt -= 1

    for loopbig in range(int(cnt)):

    # Set Fan every 15 layers
        file.write(f"M106 S{(round(Decimal((cfg.fs+cfg.fsi*loopbigcount)) * 255 / 100,0))  }\n")
        file.write(f"M104 S{round(Decimal(cfg.tsh+cfg.tih*loopbigcount),0)}\n")

        file.write(f";Layer {layer}\n")

        #Layer Marker Bottom Left
        file.write(f"G1 F{int(cfg.ps*60)} X-2 E{round(Decimal(corenermarker),5)}\n")
        file.write(f"G1 F{int(cfg.ps*60)} Y-2 E{round(Decimal(corenermarker),5)}\n")
        file.write(f"G1 F{int(cfg.ps*60)} X2 E{round(Decimal(corenermarker),5)}\n")
        file.write(f"G1 F{int(cfg.ps*60)} Y2 E{round(Decimal(corenermarker),5)}\n")


        #Begin

        #Bottom
        file.write(f"G1 F{int(cfg.ps*60)} X10 E{round(Decimal(eValueresult),5)}\n")
        file.write(f"G1 E{round(Decimal(cfg.srd+cfg.ird*0),2) * -1} F{round(Decimal((cfg.srs+cfg.irs*loopbigcount) * 60),2)}\n")
        file.write(f"G0 F{int(cfg.ts)*60} Y-10\n")
        file.write(f"G0 F{int(cfg.ts)*60} Y10\n")
        file.write(f"G1 E{round(Decimal(cfg.srd+cfg.ird*0),2)} F{round(Decimal((cfg.srs+cfg.irs*loopbigcount) * 60),2)}\n")
        file.write(f"G1 F{int(cfg.ps*60)} X10 E{round(Decimal(eValueresult),5)}\n")
        file.write(f"G1 E{round(Decimal(cfg.srd+cfg.ird*1),2) * -1} F{round(Decimal((cfg.srs+cfg.irs*loopbigcount) * 60),2)}\n")
        file.write(f"G0 F{int(cfg.ts)*60} Y-10\n")
        file.write(f"G0 F{int(cfg.ts)*60} Y10\n")
        file.write(f"G1 E{round(Decimal(cfg.srd+cfg.ird*1),2)} F{round(Decimal((cfg.srs+cfg.irs*loopbigcount) * 60),2)}\n")
        file.write(f"G1 F{int(cfg.ps*60)} X10 E{round(Decimal(eValueresult),5)}\n")
        file.write(f"G1 E{round(Decimal(cfg.srd+cfg.ird*2),2) * -1} F{round(Decimal((cfg.srs+cfg.irs*loopbigcount) * 60),2)}\n")
        file.write(f"G0 F{int(cfg.ts)*60} Y-10\n")
        file.write(f"G0 F{int(cfg.ts)*60} Y10\n")
        file.write(f"G1 E{round(Decimal(cfg.srd+cfg.ird*2),2)} F{round(Decimal((cfg.srs+cfg.irs*loopbigcount) * 60),2)}\n")
        file.write(f"G1 F{int(cfg.ps*60)} X10 E{round(Decimal(eValueresult),5)}\n")
        file.write(f"G1 E{round(Decimal(cfg.srd+cfg.ird*3),2) * -1} F{round(Decimal((cfg.srs+cfg.irs*loopbigcount) * 60),2)}\n")
        file.write(f"G0 F{int(cfg.ts)*60} Y-10\n")
        file.write(f"G0 F{int(cfg.ts)*60} Y10\n")
        file.write(f"G1 E{round(Decimal(cfg.srd+cfg.ird*3),2)} F{round(Decimal((cfg.srs+cfg.irs*loopbigcount) * 60),2)}\n")
        file.write(f"G1 F{int(cfg.ps*60)} X10 E{round(Decimal(eValueresult),5)}\n")

        #Layer Marker Bottom Right
        file.write(f"G1 F{int(cfg.ps*60)} X1 E{round(Decimal(corenermarker),5)}\n")
        file.write(f"G1 F{int(cfg.ps*60)} Y-1 E{round(Decimal(corenermarker),5)}\n")
        file.write(f"G1 F{int(cfg.ps*60)} X-1 E{round(Decimal(corenermarker),5)}\n")
        file.write(f"G1 F{int(cfg.ps*60)} Y1 E{round(Decimal(corenermarker),5)}\n")

        #Right
        file.write(f"G1 F{int(cfg.ps*60)} Y10 E{round(Decimal(eValueresult),5)}\n")
        file.write(f"G1 E{round(Decimal(cfg.srd+cfg.ird*4),2) * -1} F{round(Decimal((cfg.srs+cfg.irs*loopbigcount) * 60),2)}\n")
        file.write(f"G0 F{int(cfg.ts)*60} X10\n")
        file.write(f"G0 F{int(cfg.ts)*60} X-10\n")
        file.write(f"G1 E{round(Decimal(cfg.srd+cfg.ird*4),2)} F{round(Decimal((cfg.srs+cfg.irs*loopbigcount) * 60),2)}\n")
        file.write(f"G1 F{int(cfg.ps*60)} Y10 E{round(Decimal(eValueresult),5)}\n")
        file.write(f"G1 E{round(Decimal(cfg.srd+cfg.ird*5),2) * -1} F{round(Decimal((cfg.srs+cfg.irs*loopbigcount) * 60),2)}\n")
        file.write(f"G0 F{int(cfg.ts)*60} X10\n")
        file.write(f"G0 F{int(cfg.ts)*60} X-10\n")
        file.write(f"G1 E{round(Decimal(cfg.srd+cfg.ird*5),2)} F{round(Decimal((cfg.srs+cfg.irs*loopbigcount) * 60),2)}\n")
        file.write(f"G1 F{int(cfg.ps*60)} Y10 E{round(Decimal(eValueresult),5)}\n")
        file.write(f"G1 E{round(Decimal(cfg.srd+cfg.ird*6),2) * -1} F{round(Decimal((cfg.srs+cfg.irs*loopbigcount) * 60),2)}\n")
        file.write(f"G0 F{int(cfg.ts)*60} X10\n")
        file.write(f"G0 F{int(cfg.ts)*60} X-10\n")
        file.write(f"G1 E{round(Decimal(cfg.srd+cfg.ird*6),2)} F{round(Decimal((cfg.srs+cfg.irs*loopbigcount) * 60),2)}\n")
        file.write(f"G1 F{int(cfg.ps*60)} Y10 E{round(Decimal(eValueresult),5)}\n")
        file.write(f"G1 E{round(Decimal(cfg.srd+cfg.ird*7),2) * -1} F{round(Decimal((cfg.srs+cfg.irs*loopbigcount) * 60),2)}\n")
        file.write(f"G0 F{int(cfg.ts)*60} X10\n")
        file.write(f"G0 F{int(cfg.ts)*60} X-10\n")
        file.write(f"G1 E{round(Decimal(cfg.srd+cfg.ird*7),2)} F{round(Decimal((cfg.srs+cfg.irs*loopbigcount) * 60),2)}\n")
        file.write(f"G1 F{int(cfg.ps*60)} Y10 E{round(Decimal(eValueresult),5)}\n")

        #Layer Marker Top Right
        file.write(f"G1 F{int(cfg.ps*60)} X1 E{round(Decimal(corenermarker),5)}\n")
        file.write(f"G1 F{int(cfg.ps*60)} Y1 E{round(Decimal(corenermarker),5)}\n")
        file.write(f"G1 F{int(cfg.ps*60)} X-1 E{round(Decimal(corenermarker),5)}\n")
        file.write(f"G1 F{int(cfg.ps*60)} Y-1 E{round(Decimal(corenermarker),5)}\n")

        #Top
        file.write(f"G1 F{int(cfg.ps*60)} X-10 E{round(Decimal(eValueresult),5)}\n")
        file.write(f"G1 E{round(Decimal(cfg.srd+cfg.ird*8),2) * -1} F{round(Decimal((cfg.srs+cfg.irs*loopbigcount) * 60),2)}\n")
        file.write(f"G0 F{int(cfg.ts)*60} Y10\n")
        file.write(f"G0 F{int(cfg.ts)*60} Y-10\n")
        file.write(f"G1 E{round(Decimal(cfg.srd+cfg.ird*8),2)} F{round(Decimal((cfg.srs+cfg.irs*loopbigcount) * 60),2)}\n")
        file.write(f"G1 F{int(cfg.ps*60)} X-10 E{round(Decimal(eValueresult),5)}\n")
        file.write(f"G1 E{round(Decimal(cfg.srd+cfg.ird*9),2) * -1} F{round(Decimal((cfg.srs+cfg.irs*loopbigcount) * 60),2)}\n")
        file.write(f"G0 F{int(cfg.ts)*60} Y10\n")
        file.write(f"G0 F{int(cfg.ts)*60} Y-10\n")
        file.write(f"G1 E{round(Decimal(cfg.srd+cfg.ird*9),2)} F{round(Decimal((cfg.srs+cfg.irs*loopbigcount) * 60),2)}\n")
        file.write(f"G1 F{int(cfg.ps*60)} X-10 E{round(Decimal(eValueresult),5)}\n")
        file.write(f"G1 E{round(Decimal(cfg.srd+cfg.ird*10),2) * -1} F{round(Decimal((cfg.srs+cfg.irs*loopbigcount) * 60),2)}\n")
        file.write(f"G0 F{int(cfg.ts)*60} Y10\n")
        file.write(f"G0 F{int(cfg.ts)*60} Y-10\n")
        file.write(f"G1 E{round(Decimal(cfg.srd+cfg.ird*10),2)} F{round(Decimal((cfg.srs+cfg.irs*loopbigcount) * 60),2)}\n")
        file.write(f"G1 F{int(cfg.ps*60)} X-10 E{round(Decimal(eValueresult),5)}\n")
        file.write(f"G1 E{round(Decimal(cfg.srd+cfg.ird*11),2) * -1} F{round(Decimal((cfg.srs+cfg.irs*loopbigcount) * 60),2)}\n")
        file.write(f"G0 F{int(cfg.ts)*60} Y10\n")
        file.write(f"G0 F{int(cfg.ts)*60} Y-10\n")
        file.write(f"G1 E{round(Decimal(cfg.srd+cfg.ird*11),2)} F{round(Decimal((cfg.srs+cfg.irs*loopbigcount) * 60),2)}\n")
        file.write(f"G1 F{int(cfg.ps*60)} X-10 E{round(Decimal(eValueresult),5)}\n")

        #Layer Marker Top Left
        file.write(f"G1 F{int(cfg.ps*60)} X-1 E{round(Decimal(corenermarker),5)}\n")
        file.write(f"G1 F{int(cfg.ps*60)} Y1 E{round(Decimal(corenermarker),5)}\n")
        file.write(f"G1 F{int(cfg.ps*60)} X1 E{round(Decimal(corenermarker),5)}\n")
        file.write(f"G1 F{int(cfg.ps*60)} Y-1 E{round(Decimal(corenermarker),5)}\n")

        #Left
        file.write(f"G1 F{int(cfg.ps*60)} Y-10 E{round(Decimal(eValueresult),5)}\n")
        file.write(f"G1 E{round(Decimal(cfg.srd+cfg.ird*12),2) * -1} F{round(Decimal((cfg.srs+cfg.irs*loopbigcount) * 60),2)}\n")
        file.write(f"G0 F{int(cfg.ts)*60} X-10\n")
        file.write(f"G0 F{int(cfg.ts)*60} X10\n")
        file.write(f"G1 E{round(Decimal(cfg.srd+cfg.ird*12),2)} F{round(Decimal((cfg.srs+cfg.irs*loopbigcount) * 60),2)}\n")
        file.write(f"G1 F{int(cfg.ps*60)} Y-10 E{round(Decimal(eValueresult),5)}\n")
        file.write(f"G1 E{round(Decimal(cfg.srd+cfg.ird*13),2) * -1} F{round(Decimal((cfg.srs+cfg.irs*loopbigcount) * 60),2)}\n")
        file.write(f"G0 F{int(cfg.ts)*60} X-10\n")
        file.write(f"G0 F{int(cfg.ts)*60} X10\n")
        file.write(f"G1 E{round(Decimal(cfg.srd+cfg.ird*13),2)} F{round(Decimal((cfg.srs+cfg.irs*loopbigcount) * 60),2)}\n")
        file.write(f"G1 F{int(cfg.ps*60)} Y-10 E{round(Decimal(eValueresult),5)}\n")
        file.write(f"G1 E{round(Decimal(cfg.srd+cfg.ird*14),2) * -1} F{round(Decimal((cfg.srs+cfg.irs*loopbigcount) * 60),2)}\n")
        file.write(f"G0 F{int(cfg.ts)*60} X-10\n")
        file.write(f"G0 F{int(cfg.ts)*60} X10\n")
        file.write(f"G1 E{round(Decimal(cfg.srd+cfg.ird*14),2)} F{round(Decimal((cfg.srs+cfg.irs*loopbigcount) * 60),2)}\n")
        file.write(f"G1 F{int(cfg.ps*60)} Y-10 E{round(Decimal(eValueresult),5)}\n")
        file.write(f"G1 E{round(Decimal(cfg.srd+cfg.ird*15),2) * -1} F{round(Decimal((cfg.srs+cfg.irs*loopbigcount) * 60),2)}\n")
        file.write(f"G0 F{int(cfg.ts)*60} X-10\n")
        file.write(f"G0 F{int(cfg.ts)*60} X10\n")
        file.write(f"G1 E{round(Decimal(cfg.srd+cfg.ird*15),2)} F{round(Decimal((cfg.srs+cfg.irs*loopbigcount) * 60),2)}\n")
        file.write(f"G1 F{int(cfg.ps*60)} Y-10 E{round(Decimal(eValueresult),5)}\n")

        #Zup layer height

        file.write(f"G1 Z{cfg.lh}\n")
             
        # loopbigcount = loopbigcount +1
        layer = layer + 1


        for loopsmall in range(cfg.lt):

            file.write(f";Layer {layer}\n")
            #Bottom
            file.write(f"G1 F{int(cfg.ps*60)} X10 E{round(Decimal(eValueresult),5)}\n")
            file.write(f"G1 E{round(Decimal(cfg.srd+cfg.ird*0),2) * -1} F{round(Decimal((cfg.srs+cfg.irs*loopbigcount) * 60),2)}\n")
            file.write(f"G0 F{int(cfg.ts)*60} Y-10\n")
            file.write(f"G0 F{int(cfg.ts)*60} Y10\n")
            file.write(f"G1 E{round(Decimal(cfg.srd+cfg.ird*0),2)} F{round(Decimal((cfg.srs+cfg.irs*loopbigcount) * 60),2)}\n")
            file.write(f"G1 F{int(cfg.ps*60)} X10 E{round(Decimal(eValueresult),5)}\n")
            file.write(f"G1 E{round(Decimal(cfg.srd+cfg.ird*1),2) * -1} F{round(Decimal((cfg.srs+cfg.irs*loopbigcount) * 60),2)}\n")
            file.write(f"G0 F{int(cfg.ts)*60} Y-10\n")
            file.write(f"G0 F{int(cfg.ts)*60} Y10\n")
            file.write(f"G1 E{round(Decimal(cfg.srd+cfg.ird*1),2)} F{round(Decimal((cfg.srs+cfg.irs*loopbigcount) * 60),2)}\n")
            file.write(f"G1 F{int(cfg.ps*60)} X10 E{round(Decimal(eValueresult),5)}\n")
            file.write(f"G1 E{round(Decimal(cfg.srd+cfg.ird*2),2) * -1} F{round(Decimal((cfg.srs+cfg.irs*loopbigcount) * 60),2)}\n")
            file.write(f"G0 F{int(cfg.ts)*60} Y-10\n")
            file.write(f"G0 F{int(cfg.ts)*60} Y10\n")
            file.write(f"G1 E{round(Decimal(cfg.srd+cfg.ird*2),2)} F{round(Decimal((cfg.srs+cfg.irs*loopbigcount) * 60),2)}\n")
            file.write(f"G1 F{int(cfg.ps*60)} X10 E{round(Decimal(eValueresult),5)}\n")
            file.write(f"G1 E{round(Decimal(cfg.srd+cfg.ird*3),2) * -1} F{round(Decimal((cfg.srs+cfg.irs*loopbigcount) * 60),2)}\n")
            file.write(f"G0 F{int(cfg.ts)*60} Y-10\n")
            file.write(f"G0 F{int(cfg.ts)*60} Y10\n")
            file.write(f"G1 E{round(Decimal(cfg.srd+cfg.ird*3),2)} F{round(Decimal((cfg.srs+cfg.irs*loopbigcount) * 60),2)}\n")
            file.write(f"G1 F{int(cfg.ps*60)} X10 E{round(Decimal(eValueresult),5)}\n")

            #Right
            file.write(f"G1 F{int(cfg.ps*60)} Y10 E{round(Decimal(eValueresult),5)}\n")
            file.write(f"G1 E{round(Decimal(cfg.srd+cfg.ird*4),2) * -1} F{round(Decimal((cfg.srs+cfg.irs*loopbigcount) * 60),2)}\n")
            file.write(f"G0 F{int(cfg.ts)*60} X10\n")
            file.write(f"G0 F{int(cfg.ts)*60} X-10\n")
            file.write(f"G1 E{round(Decimal(cfg.srd+cfg.ird*4),2)} F{round(Decimal((cfg.srs+cfg.irs*loopbigcount) * 60),2)}\n")
            file.write(f"G1 F{int(cfg.ps*60)} Y10 E{round(Decimal(eValueresult),5)}\n")
            file.write(f"G1 E{round(Decimal(cfg.srd+cfg.ird*5),2) * -1} F{round(Decimal((cfg.srs+cfg.irs*loopbigcount) * 60),2)}\n")
            file.write(f"G0 F{int(cfg.ts)*60} X10\n")
            file.write(f"G0 F{int(cfg.ts)*60} X-10\n")
            file.write(f"G1 E{round(Decimal(cfg.srd+cfg.ird*5),2)} F{round(Decimal((cfg.srs+cfg.irs*loopbigcount) * 60),2)}\n")
            file.write(f"G1 F{int(cfg.ps*60)} Y10 E{round(Decimal(eValueresult),5)}\n")
            file.write(f"G1 E{round(Decimal(cfg.srd+cfg.ird*6),2) * -1} F{round(Decimal((cfg.srs+cfg.irs*loopbigcount) * 60),2)}\n")
            file.write(f"G0 F{int(cfg.ts)*60} X10\n")
            file.write(f"G0 F{int(cfg.ts)*60} X-10\n")
            file.write(f"G1 E{round(Decimal(cfg.srd+cfg.ird*6),2)} F{round(Decimal((cfg.srs+cfg.irs*loopbigcount) * 60),2)}\n")
            file.write(f"G1 F{int(cfg.ps*60)} Y10 E{round(Decimal(eValueresult),5)}\n")
            file.write(f"G1 E{round(Decimal(cfg.srd+cfg.ird*7),2) * -1} F{round(Decimal((cfg.srs+cfg.irs*loopbigcount) * 60),2)}\n")
            file.write(f"G0 F{int(cfg.ts)*60} X10\n")
            file.write(f"G0 F{int(cfg.ts)*60} X-10\n")
            file.write(f"G1 E{round(Decimal(cfg.srd+cfg.ird*7),2)} F{round(Decimal((cfg.srs+cfg.irs*loopbigcount) * 60),2)}\n")
            file.write(f"G1 F{int(cfg.ps*60)} Y10 E{round(Decimal(eValueresult),5)}\n")

            #Top
            file.write(f"G1 F{int(cfg.ps*60)} X-10 E{round(Decimal(eValueresult),5)}\n")
            file.write(f"G1 E{round(Decimal(cfg.srd+cfg.ird*8),2) * -1} F{round(Decimal((cfg.srs+cfg.irs*loopbigcount) * 60),2)}\n")
            file.write(f"G0 F{int(cfg.ts)*60} Y10\n")
            file.write(f"G0 F{int(cfg.ts)*60} Y-10\n")
            file.write(f"G1 E{round(Decimal(cfg.srd+cfg.ird*8),2)} F{round(Decimal((cfg.srs+cfg.irs*loopbigcount) * 60),2)}\n")
            file.write(f"G1 F{int(cfg.ps*60)} X-10 E{round(Decimal(eValueresult),5)}\n")
            file.write(f"G1 E{round(Decimal(cfg.srd+cfg.ird*9),2) * -1} F{round(Decimal((cfg.srs+cfg.irs*loopbigcount) * 60),2)}\n")
            file.write(f"G0 F{int(cfg.ts)*60} Y10\n")
            file.write(f"G0 F{int(cfg.ts)*60} Y-10\n")
            file.write(f"G1 E{round(Decimal(cfg.srd+cfg.ird*9),2)} F{round(Decimal((cfg.srs+cfg.irs*loopbigcount) * 60),2)}\n")
            file.write(f"G1 F{int(cfg.ps*60)} X-10 E{round(Decimal(eValueresult),5)}\n")
            file.write(f"G1 E{round(Decimal(cfg.srd+cfg.ird*10),2) * -1} F{round(Decimal((cfg.srs+cfg.irs*loopbigcount) * 60),2)}\n")
            file.write(f"G0 F{int(cfg.ts)*60} Y10\n")
            file.write(f"G0 F{int(cfg.ts)*60} Y-10\n")
            file.write(f"G1 E{round(Decimal(cfg.srd+cfg.ird*10),2)} F{round(Decimal((cfg.srs+cfg.irs*loopbigcount) * 60),2)}\n")
            file.write(f"G1 F{int(cfg.ps*60)} X-10 E{round(Decimal(eValueresult),5)}\n")
            file.write(f"G1 E{round(Decimal(cfg.srd+cfg.ird*11),2) * -1} F{round(Decimal((cfg.srs+cfg.irs*loopbigcount) * 60),2)}\n")
            file.write(f"G0 F{int(cfg.ts)*60} Y10\n")
            file.write(f"G0 F{int(cfg.ts)*60} Y-10\n")
            file.write(f"G1 E{round(Decimal(cfg.srd+cfg.ird*11),2)} F{round(Decimal((cfg.srs+cfg.irs*loopbigcount) * 60),2)}\n")
            file.write(f"G1 F{int(cfg.ps*60)} X-10 E{round(Decimal(eValueresult),5)}\n")

            #Left
            file.write(f"G1 F{int(cfg.ps*60)} Y-10 E{round(Decimal(eValueresult),5)}\n")
            file.write(f"G1 E{round(Decimal(cfg.srd+cfg.ird*12),2) * -1} F{round(Decimal((cfg.srs+cfg.irs*loopbigcount) * 60),2)}\n")
            file.write(f"G0 F{int(cfg.ts)*60} X-10\n")
            file.write(f"G0 F{int(cfg.ts)*60} X10\n")
            file.write(f"G1 E{round(Decimal(cfg.srd+cfg.ird*12),2)} F{round(Decimal((cfg.srs+cfg.irs*loopbigcount) * 60),2)}\n")
            file.write(f"G1 F{int(cfg.ps*60)} Y-10 E{round(Decimal(eValueresult),5)}\n")
            file.write(f"G1 E{round(Decimal(cfg.srd+cfg.ird*13),2) * -1} F{round(Decimal((cfg.srs+cfg.irs*loopbigcount) * 60),2)}\n")
            file.write(f"G0 F{int(cfg.ts)*60} X-10\n")
            file.write(f"G0 F{int(cfg.ts)*60} X10\n")
            file.write(f"G1 E{round(Decimal(cfg.srd+cfg.ird*13),2)} F{round(Decimal((cfg.srs+cfg.irs*loopbigcount) * 60),2)}\n")
            file.write(f"G1 F{int(cfg.ps*60)} Y-10 E{round(Decimal(eValueresult),5)}\n")
            file.write(f"G1 E{round(Decimal(cfg.srd+cfg.ird*14),2) * -1} F{round(Decimal((cfg.srs+cfg.irs*loopbigcount) * 60),2)}\n")
            file.write(f"G0 F{int(cfg.ts)*60} X-10\n")
            file.write(f"G0 F{int(cfg.ts)*60} X10\n")
            file.write(f"G1 E{round(Decimal(cfg.srd+cfg.ird*14),2)} F{round(Decimal((cfg.srs+cfg.irs*loopbigcount) * 60),2)}\n")
            file.write(f"G1 F{int(cfg.ps*60)} Y-10 E{round(Decimal(eValueresult),5)}\n")
            file.write(f"G1 E{round(Decimal(cfg.srd+cfg.ird*15),2) * -1} F{round(Decimal((cfg.srs+cfg.irs*loopbigcount) * 60),2)}\n")
            file.write(f"G0 F{int(cfg.ts)*60} X-10\n")
            file.write(f"G0 F{int(cfg.ts)*60} X10\n")
            file.write(f"G1 E{round(Decimal(cfg.srd+cfg.ird*15),2)} F{round(Decimal((cfg.srs+cfg.irs*loopbigcount) * 60),2)}\n")
            file.write(f"G1 F{int(cfg.ps*60)} Y-10 E{round(Decimal(eValueresult),5)}\n")

            file.write(f"G1 Z{cfg.lh}\n")
            layer = layer + 1

        loopbigcount = loopbigcount +1


    #End Game

    #Raise 5mm
    file.write(f"G1 Z5\n")
    #Absolute Position
    file.write(f"G90\n")
    #Home X Y
    file.write(f"G28 X0 Y0\n")
    #Turn off Steppers
    file.write(f"M84\n")
    #Turn off Fan
    file.write(f"M107\n")
    #Turn off Hotend
    file.write(f"M104 S0\n")
    #Turn off Bed
    file.write(f"M140 S0\n")

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
    