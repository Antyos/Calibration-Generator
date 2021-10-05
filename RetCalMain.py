# -*- coding: utf-8 -*-

from dataclasses import dataclass

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
    )
    
    # Array of retraction distances
    retraction_dist = [round(Decimal(cfg.srd + cfg.ird * i), 2) for i in range(16)]
    
    file.write(f";Calibration Generator 1.3.3\n")
    file.write(f";\n")
    file.write(f";\n")
    file.write(f";Retraction Distance from the top looking down\n")
    file.write(f";\n")
    file.write(f";       {retraction_dist[11]}    {retraction_dist[10]}    {retraction_dist[9]}    {retraction_dist[8]}\n")
    file.write(f";		|		|		|		|\n")
    file.write(f";\n")
    file.write(f";{retraction_dist[12]}-                               -{retraction_dist[7]}\n")
    file.write(f";\n")
    file.write(f";\n")
    file.write(f";{retraction_dist[13]}-                               -{retraction_dist[6]}\n")
    file.write(f";\n")
    file.write(f";\n")
    file.write(f";{retraction_dist[14]}-                               -{retraction_dist[5]}\n")
    file.write(f";\n")
    file.write(f";\n")
    file.write(f";{retraction_dist[15]}-                               -{retraction_dist[4]}\n")
    file.write(f";\n")
    file.write(f";		|		|		|		|\n")
    file.write(f";       {retraction_dist[0]}    {retraction_dist[1]}    {retraction_dist[2]}    {retraction_dist[3]}\n")
    file.write(f";\n")
    file.write(f";\n")


    file.write(f";Variables by Height\n")
    file.write(f";\n")
    file.write(f";Height         Retraction  Nozzle      Fan\n")
    file.write(f";               Speed       Temp        Speed\n")
    file.write(f";\n")

    cnt = cfg.nt-1

    for loopx in range(cfg.nt):
        file.write(f";{cfg.lt} layers      {round(Decimal(cfg.srs+cfg.irs*cnt),2)}      {round(Decimal(cfg.tsh+cfg.tih*cnt),2)}      {round(Decimal(cfg.fs+cfg.fsi*cnt),2)}\n")
        cnt = cnt-1


    dx = float(ui.dimensionX.text())
    dy = float(ui.dimensionY.text())
    ps = float(ui.printSpeed.text())
    nd = float(ui.nozzleDiameter.text())
    fd = float(ui.filamentDiameter.text())
    em = float(ui.extrusionMultiplier.text())
    tb = float(ui.tempBed.text())

    # Custom Gcode
    sgcode = str(ui.customGcode.toPlainText())


    file.write(f";\n")
    file.write(f";\n")
    file.write(f";All inputs\n")
    file.write(f";\n")
    file.write(f";Dimension X 					{int(dx)}\n")
    file.write(f";Dimension Y 					{int(dy)}\n")
    file.write(f";Starting Retraction Distance	{cfg.srd}\n")
    file.write(f";Increment Retraction 			{cfg.ird}\n")
    file.write(f";Start Retraction Speed 		{cfg.srs}\n")
    file.write(f";Retraction Speed Increment 	{cfg.irs}\n")
    file.write(f";Print Speed 					{ps}\n")
    file.write(f";Starting Temp 					{int(cfg.tsh)}\n")
    file.write(f";Increment Temp 				{int(cfg.tih)}\n")
    file.write(f";Bed Temp 						{int(tb)}\n")
    file.write(f";Fan Speed 						{int(cfg.fs)}\n")
    file.write(f";Fan Speed Increment 			{int(cfg.fsi)}\n")
    file.write(f";Nozzle Diameter 				{nd}\n")
    file.write(f";Layer Height 					{cfg.lh}\n")
    file.write(f";Filament Diameter 				{fd}\n")
    file.write(f";Extrusion Multiplier 			{em}\n")
    file.write(f";Layers Per Test                {cfg.lt}\n")
    file.write(f";Number of Tests                {cfg.nt}\n")
    file.write(f";\n")
    file.write(f";\n")


    # Generate E Value  https://3dprinting.stackexchange.com/questions/10171/how-is-e-value-calculated-in-slic3r

    def eValue ( extrusionLength ):

        diameterNozzle = float(ui.nozzleDiameter.text())
        heightLayer = float(ui.layerHeight.text())
        diameterFilament = float(ui.filamentDiameter.text())
        multiplierExtrusion = float(ui.extrusionMultiplier.text())

        area = (diameterNozzle - heightLayer) * heightLayer + 3.14159 * (heightLayer/2)**2
        eValueresult = (area * extrusionLength * 4)/(3.14159 * diameterFilament**2/multiplierExtrusion)
        return eValueresult


    #start Gcode
    file.write(f";Start Gcode\n")
    file.write(f"M140 S{int(tb)}\n")
    file.write(f"M105\n")
    file.write(f"M190 S{int(tb)}\n")
    file.write(f"M104 S{int(cfg.tsh)}\n")
    file.write(f"M105\n")
    file.write(f"M109 S{int(cfg.tsh)}\n")
    file.write(f"M82\n")
    file.write(f"G28\n")
    file.write(f"G92 E0\n")
    file.write(f"G1 F200 E1\n")
    file.write(f"G92 E0\n")

    file.write(f"{sgcode}\n")

    file.write(f";\n")
    file.write(f";\n")

    xpos = dx/2-30
    ypos = dy/2-30
    zpos = cfg.lh
    epos = 0



    #Start Movement
    file.write(f";Start Movement\n")
    file.write(f";\n")
    file.write(f"G1 Z2\n")
    file.write(f"G1 F{int(cfg.ts)*60} X{xpos} Y{ypos} Z{zpos}\n")
    file.write(f";\n")
    eValueresult = eValue(60)

    #Overextruding Raft
    evalueincrease = eValueresult*1.25
    eValueresult = evalueincrease


    remx = xpos
    remy = ypos

    file.write(f";Layer 1\n")

    #Horizontal

    for loopx in range(30):
        file.write(f"G1 F{int(ps*60/2)} X{xpos+60} Y{ypos} E{round(Decimal(eValueresult),5)}\n")
        xpos = xpos + 60
        eValueresult = eValueresult + evalueincrease
        file.write(f"G0 F{int(cfg.ts)*60} X{xpos} Y{ypos+1}\n")
        ypos = ypos + 1
        file.write(f"G1 F{int(ps*60/2)} X{xpos-60} Y{ypos} E{round(Decimal(eValueresult),5)}\n")
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
        file.write(f"G1 F{int(ps*60/2)} X{xpos} Y{ypos+60} E{round(Decimal(eValueresult),5)}\n")
        ypos = ypos + 60
        eValueresult = eValueresult + evalueincrease
        file.write(f"G0 F{int(cfg.ts)*60} X{xpos+1} Y{ypos}\n")
        xpos = xpos + 1
        file.write(f"G1 F{int(ps*60/2)} X{xpos} Y{ypos-60} E{round(Decimal(eValueresult),5)}\n")
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

    eValueresult = eValue(10)
    corenermarker = eValue(1)

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
        file.write(f"G1 F{int(ps*60)} X-2 E{round(Decimal(corenermarker),5)}\n")
        file.write(f"G1 F{int(ps*60)} Y-2 E{round(Decimal(corenermarker),5)}\n")
        file.write(f"G1 F{int(ps*60)} X2 E{round(Decimal(corenermarker),5)}\n")
        file.write(f"G1 F{int(ps*60)} Y2 E{round(Decimal(corenermarker),5)}\n")


        #Begin

        #Bottom
        file.write(f"G1 F{int(ps*60)} X10 E{round(Decimal(eValueresult),5)}\n")
        file.write(f"G1 E{round(Decimal(cfg.srd+cfg.ird*0),2) * -1} F{round(Decimal((cfg.srs+cfg.irs*loopbigcount) * 60),2)}\n")
        file.write(f"G0 F{int(cfg.ts)*60} Y-10\n")
        file.write(f"G0 F{int(cfg.ts)*60} Y10\n")
        file.write(f"G1 E{round(Decimal(cfg.srd+cfg.ird*0),2)} F{round(Decimal((cfg.srs+cfg.irs*loopbigcount) * 60),2)}\n")
        file.write(f"G1 F{int(ps*60)} X10 E{round(Decimal(eValueresult),5)}\n")
        file.write(f"G1 E{round(Decimal(cfg.srd+cfg.ird*1),2) * -1} F{round(Decimal((cfg.srs+cfg.irs*loopbigcount) * 60),2)}\n")
        file.write(f"G0 F{int(cfg.ts)*60} Y-10\n")
        file.write(f"G0 F{int(cfg.ts)*60} Y10\n")
        file.write(f"G1 E{round(Decimal(cfg.srd+cfg.ird*1),2)} F{round(Decimal((cfg.srs+cfg.irs*loopbigcount) * 60),2)}\n")
        file.write(f"G1 F{int(ps*60)} X10 E{round(Decimal(eValueresult),5)}\n")
        file.write(f"G1 E{round(Decimal(cfg.srd+cfg.ird*2),2) * -1} F{round(Decimal((cfg.srs+cfg.irs*loopbigcount) * 60),2)}\n")
        file.write(f"G0 F{int(cfg.ts)*60} Y-10\n")
        file.write(f"G0 F{int(cfg.ts)*60} Y10\n")
        file.write(f"G1 E{round(Decimal(cfg.srd+cfg.ird*2),2)} F{round(Decimal((cfg.srs+cfg.irs*loopbigcount) * 60),2)}\n")
        file.write(f"G1 F{int(ps*60)} X10 E{round(Decimal(eValueresult),5)}\n")
        file.write(f"G1 E{round(Decimal(cfg.srd+cfg.ird*3),2) * -1} F{round(Decimal((cfg.srs+cfg.irs*loopbigcount) * 60),2)}\n")
        file.write(f"G0 F{int(cfg.ts)*60} Y-10\n")
        file.write(f"G0 F{int(cfg.ts)*60} Y10\n")
        file.write(f"G1 E{round(Decimal(cfg.srd+cfg.ird*3),2)} F{round(Decimal((cfg.srs+cfg.irs*loopbigcount) * 60),2)}\n")
        file.write(f"G1 F{int(ps*60)} X10 E{round(Decimal(eValueresult),5)}\n")

        #Layer Marker Bottom Right
        file.write(f"G1 F{int(ps*60)} X1 E{round(Decimal(corenermarker),5)}\n")
        file.write(f"G1 F{int(ps*60)} Y-1 E{round(Decimal(corenermarker),5)}\n")
        file.write(f"G1 F{int(ps*60)} X-1 E{round(Decimal(corenermarker),5)}\n")
        file.write(f"G1 F{int(ps*60)} Y1 E{round(Decimal(corenermarker),5)}\n")

        #Right
        file.write(f"G1 F{int(ps*60)} Y10 E{round(Decimal(eValueresult),5)}\n")
        file.write(f"G1 E{round(Decimal(cfg.srd+cfg.ird*4),2) * -1} F{round(Decimal((cfg.srs+cfg.irs*loopbigcount) * 60),2)}\n")
        file.write(f"G0 F{int(cfg.ts)*60} X10\n")
        file.write(f"G0 F{int(cfg.ts)*60} X-10\n")
        file.write(f"G1 E{round(Decimal(cfg.srd+cfg.ird*4),2)} F{round(Decimal((cfg.srs+cfg.irs*loopbigcount) * 60),2)}\n")
        file.write(f"G1 F{int(ps*60)} Y10 E{round(Decimal(eValueresult),5)}\n")
        file.write(f"G1 E{round(Decimal(cfg.srd+cfg.ird*5),2) * -1} F{round(Decimal((cfg.srs+cfg.irs*loopbigcount) * 60),2)}\n")
        file.write(f"G0 F{int(cfg.ts)*60} X10\n")
        file.write(f"G0 F{int(cfg.ts)*60} X-10\n")
        file.write(f"G1 E{round(Decimal(cfg.srd+cfg.ird*5),2)} F{round(Decimal((cfg.srs+cfg.irs*loopbigcount) * 60),2)}\n")
        file.write(f"G1 F{int(ps*60)} Y10 E{round(Decimal(eValueresult),5)}\n")
        file.write(f"G1 E{round(Decimal(cfg.srd+cfg.ird*6),2) * -1} F{round(Decimal((cfg.srs+cfg.irs*loopbigcount) * 60),2)}\n")
        file.write(f"G0 F{int(cfg.ts)*60} X10\n")
        file.write(f"G0 F{int(cfg.ts)*60} X-10\n")
        file.write(f"G1 E{round(Decimal(cfg.srd+cfg.ird*6),2)} F{round(Decimal((cfg.srs+cfg.irs*loopbigcount) * 60),2)}\n")
        file.write(f"G1 F{int(ps*60)} Y10 E{round(Decimal(eValueresult),5)}\n")
        file.write(f"G1 E{round(Decimal(cfg.srd+cfg.ird*7),2) * -1} F{round(Decimal((cfg.srs+cfg.irs*loopbigcount) * 60),2)}\n")
        file.write(f"G0 F{int(cfg.ts)*60} X10\n")
        file.write(f"G0 F{int(cfg.ts)*60} X-10\n")
        file.write(f"G1 E{round(Decimal(cfg.srd+cfg.ird*7),2)} F{round(Decimal((cfg.srs+cfg.irs*loopbigcount) * 60),2)}\n")
        file.write(f"G1 F{int(ps*60)} Y10 E{round(Decimal(eValueresult),5)}\n")

        #Layer Marker Top Right
        file.write(f"G1 F{int(ps*60)} X1 E{round(Decimal(corenermarker),5)}\n")
        file.write(f"G1 F{int(ps*60)} Y1 E{round(Decimal(corenermarker),5)}\n")
        file.write(f"G1 F{int(ps*60)} X-1 E{round(Decimal(corenermarker),5)}\n")
        file.write(f"G1 F{int(ps*60)} Y-1 E{round(Decimal(corenermarker),5)}\n")

        #Top
        file.write(f"G1 F{int(ps*60)} X-10 E{round(Decimal(eValueresult),5)}\n")
        file.write(f"G1 E{round(Decimal(cfg.srd+cfg.ird*8),2) * -1} F{round(Decimal((cfg.srs+cfg.irs*loopbigcount) * 60),2)}\n")
        file.write(f"G0 F{int(cfg.ts)*60} Y10\n")
        file.write(f"G0 F{int(cfg.ts)*60} Y-10\n")
        file.write(f"G1 E{round(Decimal(cfg.srd+cfg.ird*8),2)} F{round(Decimal((cfg.srs+cfg.irs*loopbigcount) * 60),2)}\n")
        file.write(f"G1 F{int(ps*60)} X-10 E{round(Decimal(eValueresult),5)}\n")
        file.write(f"G1 E{round(Decimal(cfg.srd+cfg.ird*9),2) * -1} F{round(Decimal((cfg.srs+cfg.irs*loopbigcount) * 60),2)}\n")
        file.write(f"G0 F{int(cfg.ts)*60} Y10\n")
        file.write(f"G0 F{int(cfg.ts)*60} Y-10\n")
        file.write(f"G1 E{round(Decimal(cfg.srd+cfg.ird*9),2)} F{round(Decimal((cfg.srs+cfg.irs*loopbigcount) * 60),2)}\n")
        file.write(f"G1 F{int(ps*60)} X-10 E{round(Decimal(eValueresult),5)}\n")
        file.write(f"G1 E{round(Decimal(cfg.srd+cfg.ird*10),2) * -1} F{round(Decimal((cfg.srs+cfg.irs*loopbigcount) * 60),2)}\n")
        file.write(f"G0 F{int(cfg.ts)*60} Y10\n")
        file.write(f"G0 F{int(cfg.ts)*60} Y-10\n")
        file.write(f"G1 E{round(Decimal(cfg.srd+cfg.ird*10),2)} F{round(Decimal((cfg.srs+cfg.irs*loopbigcount) * 60),2)}\n")
        file.write(f"G1 F{int(ps*60)} X-10 E{round(Decimal(eValueresult),5)}\n")
        file.write(f"G1 E{round(Decimal(cfg.srd+cfg.ird*11),2) * -1} F{round(Decimal((cfg.srs+cfg.irs*loopbigcount) * 60),2)}\n")
        file.write(f"G0 F{int(cfg.ts)*60} Y10\n")
        file.write(f"G0 F{int(cfg.ts)*60} Y-10\n")
        file.write(f"G1 E{round(Decimal(cfg.srd+cfg.ird*11),2)} F{round(Decimal((cfg.srs+cfg.irs*loopbigcount) * 60),2)}\n")
        file.write(f"G1 F{int(ps*60)} X-10 E{round(Decimal(eValueresult),5)}\n")

        #Layer Marker Top Left
        file.write(f"G1 F{int(ps*60)} X-1 E{round(Decimal(corenermarker),5)}\n")
        file.write(f"G1 F{int(ps*60)} Y1 E{round(Decimal(corenermarker),5)}\n")
        file.write(f"G1 F{int(ps*60)} X1 E{round(Decimal(corenermarker),5)}\n")
        file.write(f"G1 F{int(ps*60)} Y-1 E{round(Decimal(corenermarker),5)}\n")

        #Left
        file.write(f"G1 F{int(ps*60)} Y-10 E{round(Decimal(eValueresult),5)}\n")
        file.write(f"G1 E{round(Decimal(cfg.srd+cfg.ird*12),2) * -1} F{round(Decimal((cfg.srs+cfg.irs*loopbigcount) * 60),2)}\n")
        file.write(f"G0 F{int(cfg.ts)*60} X-10\n")
        file.write(f"G0 F{int(cfg.ts)*60} X10\n")
        file.write(f"G1 E{round(Decimal(cfg.srd+cfg.ird*12),2)} F{round(Decimal((cfg.srs+cfg.irs*loopbigcount) * 60),2)}\n")
        file.write(f"G1 F{int(ps*60)} Y-10 E{round(Decimal(eValueresult),5)}\n")
        file.write(f"G1 E{round(Decimal(cfg.srd+cfg.ird*13),2) * -1} F{round(Decimal((cfg.srs+cfg.irs*loopbigcount) * 60),2)}\n")
        file.write(f"G0 F{int(cfg.ts)*60} X-10\n")
        file.write(f"G0 F{int(cfg.ts)*60} X10\n")
        file.write(f"G1 E{round(Decimal(cfg.srd+cfg.ird*13),2)} F{round(Decimal((cfg.srs+cfg.irs*loopbigcount) * 60),2)}\n")
        file.write(f"G1 F{int(ps*60)} Y-10 E{round(Decimal(eValueresult),5)}\n")
        file.write(f"G1 E{round(Decimal(cfg.srd+cfg.ird*14),2) * -1} F{round(Decimal((cfg.srs+cfg.irs*loopbigcount) * 60),2)}\n")
        file.write(f"G0 F{int(cfg.ts)*60} X-10\n")
        file.write(f"G0 F{int(cfg.ts)*60} X10\n")
        file.write(f"G1 E{round(Decimal(cfg.srd+cfg.ird*14),2)} F{round(Decimal((cfg.srs+cfg.irs*loopbigcount) * 60),2)}\n")
        file.write(f"G1 F{int(ps*60)} Y-10 E{round(Decimal(eValueresult),5)}\n")
        file.write(f"G1 E{round(Decimal(cfg.srd+cfg.ird*15),2) * -1} F{round(Decimal((cfg.srs+cfg.irs*loopbigcount) * 60),2)}\n")
        file.write(f"G0 F{int(cfg.ts)*60} X-10\n")
        file.write(f"G0 F{int(cfg.ts)*60} X10\n")
        file.write(f"G1 E{round(Decimal(cfg.srd+cfg.ird*15),2)} F{round(Decimal((cfg.srs+cfg.irs*loopbigcount) * 60),2)}\n")
        file.write(f"G1 F{int(ps*60)} Y-10 E{round(Decimal(eValueresult),5)}\n")

        #Zup layer height

        file.write(f"G1 Z{cfg.lh}\n")
             
        # loopbigcount = loopbigcount +1
        layer = layer + 1


        for loopsmall in range(cfg.lt):

            file.write(f";Layer {layer}\n")
            #Bottom
            file.write(f"G1 F{int(ps*60)} X10 E{round(Decimal(eValueresult),5)}\n")
            file.write(f"G1 E{round(Decimal(cfg.srd+cfg.ird*0),2) * -1} F{round(Decimal((cfg.srs+cfg.irs*loopbigcount) * 60),2)}\n")
            file.write(f"G0 F{int(cfg.ts)*60} Y-10\n")
            file.write(f"G0 F{int(cfg.ts)*60} Y10\n")
            file.write(f"G1 E{round(Decimal(cfg.srd+cfg.ird*0),2)} F{round(Decimal((cfg.srs+cfg.irs*loopbigcount) * 60),2)}\n")
            file.write(f"G1 F{int(ps*60)} X10 E{round(Decimal(eValueresult),5)}\n")
            file.write(f"G1 E{round(Decimal(cfg.srd+cfg.ird*1),2) * -1} F{round(Decimal((cfg.srs+cfg.irs*loopbigcount) * 60),2)}\n")
            file.write(f"G0 F{int(cfg.ts)*60} Y-10\n")
            file.write(f"G0 F{int(cfg.ts)*60} Y10\n")
            file.write(f"G1 E{round(Decimal(cfg.srd+cfg.ird*1),2)} F{round(Decimal((cfg.srs+cfg.irs*loopbigcount) * 60),2)}\n")
            file.write(f"G1 F{int(ps*60)} X10 E{round(Decimal(eValueresult),5)}\n")
            file.write(f"G1 E{round(Decimal(cfg.srd+cfg.ird*2),2) * -1} F{round(Decimal((cfg.srs+cfg.irs*loopbigcount) * 60),2)}\n")
            file.write(f"G0 F{int(cfg.ts)*60} Y-10\n")
            file.write(f"G0 F{int(cfg.ts)*60} Y10\n")
            file.write(f"G1 E{round(Decimal(cfg.srd+cfg.ird*2),2)} F{round(Decimal((cfg.srs+cfg.irs*loopbigcount) * 60),2)}\n")
            file.write(f"G1 F{int(ps*60)} X10 E{round(Decimal(eValueresult),5)}\n")
            file.write(f"G1 E{round(Decimal(cfg.srd+cfg.ird*3),2) * -1} F{round(Decimal((cfg.srs+cfg.irs*loopbigcount) * 60),2)}\n")
            file.write(f"G0 F{int(cfg.ts)*60} Y-10\n")
            file.write(f"G0 F{int(cfg.ts)*60} Y10\n")
            file.write(f"G1 E{round(Decimal(cfg.srd+cfg.ird*3),2)} F{round(Decimal((cfg.srs+cfg.irs*loopbigcount) * 60),2)}\n")
            file.write(f"G1 F{int(ps*60)} X10 E{round(Decimal(eValueresult),5)}\n")

            #Right
            file.write(f"G1 F{int(ps*60)} Y10 E{round(Decimal(eValueresult),5)}\n")
            file.write(f"G1 E{round(Decimal(cfg.srd+cfg.ird*4),2) * -1} F{round(Decimal((cfg.srs+cfg.irs*loopbigcount) * 60),2)}\n")
            file.write(f"G0 F{int(cfg.ts)*60} X10\n")
            file.write(f"G0 F{int(cfg.ts)*60} X-10\n")
            file.write(f"G1 E{round(Decimal(cfg.srd+cfg.ird*4),2)} F{round(Decimal((cfg.srs+cfg.irs*loopbigcount) * 60),2)}\n")
            file.write(f"G1 F{int(ps*60)} Y10 E{round(Decimal(eValueresult),5)}\n")
            file.write(f"G1 E{round(Decimal(cfg.srd+cfg.ird*5),2) * -1} F{round(Decimal((cfg.srs+cfg.irs*loopbigcount) * 60),2)}\n")
            file.write(f"G0 F{int(cfg.ts)*60} X10\n")
            file.write(f"G0 F{int(cfg.ts)*60} X-10\n")
            file.write(f"G1 E{round(Decimal(cfg.srd+cfg.ird*5),2)} F{round(Decimal((cfg.srs+cfg.irs*loopbigcount) * 60),2)}\n")
            file.write(f"G1 F{int(ps*60)} Y10 E{round(Decimal(eValueresult),5)}\n")
            file.write(f"G1 E{round(Decimal(cfg.srd+cfg.ird*6),2) * -1} F{round(Decimal((cfg.srs+cfg.irs*loopbigcount) * 60),2)}\n")
            file.write(f"G0 F{int(cfg.ts)*60} X10\n")
            file.write(f"G0 F{int(cfg.ts)*60} X-10\n")
            file.write(f"G1 E{round(Decimal(cfg.srd+cfg.ird*6),2)} F{round(Decimal((cfg.srs+cfg.irs*loopbigcount) * 60),2)}\n")
            file.write(f"G1 F{int(ps*60)} Y10 E{round(Decimal(eValueresult),5)}\n")
            file.write(f"G1 E{round(Decimal(cfg.srd+cfg.ird*7),2) * -1} F{round(Decimal((cfg.srs+cfg.irs*loopbigcount) * 60),2)}\n")
            file.write(f"G0 F{int(cfg.ts)*60} X10\n")
            file.write(f"G0 F{int(cfg.ts)*60} X-10\n")
            file.write(f"G1 E{round(Decimal(cfg.srd+cfg.ird*7),2)} F{round(Decimal((cfg.srs+cfg.irs*loopbigcount) * 60),2)}\n")
            file.write(f"G1 F{int(ps*60)} Y10 E{round(Decimal(eValueresult),5)}\n")

            #Top
            file.write(f"G1 F{int(ps*60)} X-10 E{round(Decimal(eValueresult),5)}\n")
            file.write(f"G1 E{round(Decimal(cfg.srd+cfg.ird*8),2) * -1} F{round(Decimal((cfg.srs+cfg.irs*loopbigcount) * 60),2)}\n")
            file.write(f"G0 F{int(cfg.ts)*60} Y10\n")
            file.write(f"G0 F{int(cfg.ts)*60} Y-10\n")
            file.write(f"G1 E{round(Decimal(cfg.srd+cfg.ird*8),2)} F{round(Decimal((cfg.srs+cfg.irs*loopbigcount) * 60),2)}\n")
            file.write(f"G1 F{int(ps*60)} X-10 E{round(Decimal(eValueresult),5)}\n")
            file.write(f"G1 E{round(Decimal(cfg.srd+cfg.ird*9),2) * -1} F{round(Decimal((cfg.srs+cfg.irs*loopbigcount) * 60),2)}\n")
            file.write(f"G0 F{int(cfg.ts)*60} Y10\n")
            file.write(f"G0 F{int(cfg.ts)*60} Y-10\n")
            file.write(f"G1 E{round(Decimal(cfg.srd+cfg.ird*9),2)} F{round(Decimal((cfg.srs+cfg.irs*loopbigcount) * 60),2)}\n")
            file.write(f"G1 F{int(ps*60)} X-10 E{round(Decimal(eValueresult),5)}\n")
            file.write(f"G1 E{round(Decimal(cfg.srd+cfg.ird*10),2) * -1} F{round(Decimal((cfg.srs+cfg.irs*loopbigcount) * 60),2)}\n")
            file.write(f"G0 F{int(cfg.ts)*60} Y10\n")
            file.write(f"G0 F{int(cfg.ts)*60} Y-10\n")
            file.write(f"G1 E{round(Decimal(cfg.srd+cfg.ird*10),2)} F{round(Decimal((cfg.srs+cfg.irs*loopbigcount) * 60),2)}\n")
            file.write(f"G1 F{int(ps*60)} X-10 E{round(Decimal(eValueresult),5)}\n")
            file.write(f"G1 E{round(Decimal(cfg.srd+cfg.ird*11),2) * -1} F{round(Decimal((cfg.srs+cfg.irs*loopbigcount) * 60),2)}\n")
            file.write(f"G0 F{int(cfg.ts)*60} Y10\n")
            file.write(f"G0 F{int(cfg.ts)*60} Y-10\n")
            file.write(f"G1 E{round(Decimal(cfg.srd+cfg.ird*11),2)} F{round(Decimal((cfg.srs+cfg.irs*loopbigcount) * 60),2)}\n")
            file.write(f"G1 F{int(ps*60)} X-10 E{round(Decimal(eValueresult),5)}\n")

            #Left
            file.write(f"G1 F{int(ps*60)} Y-10 E{round(Decimal(eValueresult),5)}\n")
            file.write(f"G1 E{round(Decimal(cfg.srd+cfg.ird*12),2) * -1} F{round(Decimal((cfg.srs+cfg.irs*loopbigcount) * 60),2)}\n")
            file.write(f"G0 F{int(cfg.ts)*60} X-10\n")
            file.write(f"G0 F{int(cfg.ts)*60} X10\n")
            file.write(f"G1 E{round(Decimal(cfg.srd+cfg.ird*12),2)} F{round(Decimal((cfg.srs+cfg.irs*loopbigcount) * 60),2)}\n")
            file.write(f"G1 F{int(ps*60)} Y-10 E{round(Decimal(eValueresult),5)}\n")
            file.write(f"G1 E{round(Decimal(cfg.srd+cfg.ird*13),2) * -1} F{round(Decimal((cfg.srs+cfg.irs*loopbigcount) * 60),2)}\n")
            file.write(f"G0 F{int(cfg.ts)*60} X-10\n")
            file.write(f"G0 F{int(cfg.ts)*60} X10\n")
            file.write(f"G1 E{round(Decimal(cfg.srd+cfg.ird*13),2)} F{round(Decimal((cfg.srs+cfg.irs*loopbigcount) * 60),2)}\n")
            file.write(f"G1 F{int(ps*60)} Y-10 E{round(Decimal(eValueresult),5)}\n")
            file.write(f"G1 E{round(Decimal(cfg.srd+cfg.ird*14),2) * -1} F{round(Decimal((cfg.srs+cfg.irs*loopbigcount) * 60),2)}\n")
            file.write(f"G0 F{int(cfg.ts)*60} X-10\n")
            file.write(f"G0 F{int(cfg.ts)*60} X10\n")
            file.write(f"G1 E{round(Decimal(cfg.srd+cfg.ird*14),2)} F{round(Decimal((cfg.srs+cfg.irs*loopbigcount) * 60),2)}\n")
            file.write(f"G1 F{int(ps*60)} Y-10 E{round(Decimal(eValueresult),5)}\n")
            file.write(f"G1 E{round(Decimal(cfg.srd+cfg.ird*15),2) * -1} F{round(Decimal((cfg.srs+cfg.irs*loopbigcount) * 60),2)}\n")
            file.write(f"G0 F{int(cfg.ts)*60} X-10\n")
            file.write(f"G0 F{int(cfg.ts)*60} X10\n")
            file.write(f"G1 E{round(Decimal(cfg.srd+cfg.ird*15),2)} F{round(Decimal((cfg.srs+cfg.irs*loopbigcount) * 60),2)}\n")
            file.write(f"G1 F{int(ps*60)} Y-10 E{round(Decimal(eValueresult),5)}\n")

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
