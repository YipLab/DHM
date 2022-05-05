#!/usr/bin/env python3

import os.path
import sys

import dhm.core
import dhm.interactive
import dhm.utils
import dhm.dhmtry

from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QDialog, QApplication, QPushButton, QVBoxLayout
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt


class Launcher(QtWidgets.QMainWindow):
    def __init__(self):
        super(Launcher, self).__init__()  # Call the inherited classes __init__ method
        uic.loadUi('./ui_files/launcher_window.ui', self)  # Load the .ui file

        self.std_TDHM = TdhmWidgetStd()

        self.standard_TDHM.clicked.connect(self.std_TDHM.show)


class TdhmWidgetStd(QtWidgets.QWidget):
    def __init__(self):
        super(TdhmWidgetStd, self).__init__()  # Call the inherited classes __init__ method
        uic.loadUi('./ui_files/tdhm_widget_std.ui', self)  # Load the .ui file

        self.SysCalibration = SysCalib()
        self.Parameter = ParamSet()

        self.pushButton_calibration.clicked.connect(self.sys_calibration)
        self.pushButton_parameter.clicked.connect(self.parameter_set)
        self.radioButton_liveimg.toggled.connect(self.live_image_check)

    def sys_calibration(self):
        self.SysCalibration.show()
        self.checkBox_calibration.setChecked(True)

    def parameter_set(self):
        self.Parameter.show()
        self.checkBox_parameter.setChecked(True)

    def live_image_check(self):
        if self.radioButton_liveimg.isChecked():
            self.pushButton_read_add.hide()
            self.label_read_add.hide()
            self.lineEdit_read_add.hide()
        else:
            self.pushButton_read_add.show()
            self.label_read_add.show()
            self.lineEdit_read_add.show()


class SysCalib(QtWidgets.QDialog):
    def __init__(self):
        super(SysCalib, self).__init__()  # Call the inherited classes __init__ method
        uic.loadUi('./ui_files/sys_calib_dialog.ui', self)  # Load the .ui file


class ParamSet(QtWidgets.QDialog):
    def __init__(self):
        super(ParamSet, self).__init__()  # Call the inherited classes __init__ method
        uic.loadUi('./ui_files/param_set_dialog.ui', self)  # Load the .ui file

        self.pushButton_confirm.clicked.connect(self.param_set_confirm)
        self.pushButton_cancel.clicked.connect(self.param_set_cancel)

        self.dhmcore = dhm.dhmtry.HoloGram()

    def param_set_confirm(self):
        self.dhmcore.set_sys_param(pixel_x=self.pixel_size.value(),
                                   pixel_y=self.pixel_size.value(),
                                   refractive_index=self.refractive_index.value(),
                                   magnification=self.magnification.value(),
                                   wavelength=self.wave_length.value())
        #self.dhmcore._pixel_x = self.pixel_size.value()
        self.close()

    def param_set_cancel(self):
        self.close()



if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)  # Create an instance of QtWidgets.QApplication
    launcher = Launcher()  # Create an instance of our class
    launcher.show()

    sys.exit(app.exec())
