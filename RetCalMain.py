# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtGui, QtWidgets
from RetCalui import Ui_MainWindow

from retcal.generate_ret_cal import GcodeConfig, generate_retraction_calibration


def button_clicked(ui: Ui_MainWindow):
    name = QtWidgets.QFileDialog.getSaveFileName(
        ui.centralwidget, "Save Gcode", filter="(*.gcode)"
    )

    # Return if no file name
    if len(name[0]) == 0:
        return

    filename = name[0]

    # Get config
    config = GcodeConfig(
        # Start Gcode Retraction Distance
        retraction_dist_init=float(ui.startRetractiondistance.text()),
        retraction_dist_delta=float(ui.incrementRetractiondistance.text()),
        # Variables by Height
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

    with open(filename, "w") as file:
        for line in generate_retraction_calibration(config):
            file.write(f"{line}\n")


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
