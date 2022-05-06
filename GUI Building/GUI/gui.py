#!/usr/bin/env python3

import os.path
import sys
from tkinter.filedialog import askdirectory
import dhm.core
import dhm.interactive
import dhm.utils

from PyQt5 import QtWidgets, uic, QtCore, QtGui
from qt_material import apply_stylesheet
import qdarkstyle
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

        self.save_path = None
        self.read_path = None

        self.SysCalibration = SysCalib()
        self.Parameter = ParamSet()

        self.pushButton_start.hide()
        self.pushButton_calibration.clicked.connect(self.sys_calibration)
        self.pushButton_parameter.clicked.connect(self.parameter_set)
        self.radioButton_liveimg.toggled.connect(self.live_image_check)
        self.pushButton_read_add.clicked.connect(self.add_read)
        self.pushButton_save_add.clicked.connect(self.add_save)
        self.checkBox_calibration.stateChanged.connect(self.sop_check)
        self.checkBox_parameter.stateChanged.connect(self.sop_check)

        # self.pushButton_start.clicked.connect(self.start)

    def sop_check(self):
        if self.checkBox_parameter.isChecked():
            if self.checkBox_calibration.isChecked():
                self.pushButton_start.show()
            else:
                self.pushButton_start.hide()
        else:
            self.pushButton_start.hide()

    def sys_calibration(self):
        self.SysCalibration.show()
        self.checkBox_calibration.setChecked(True)

    def parameter_set(self):
        self.Parameter.show()
        self.checkBox_parameter.setChecked(True)

    def add_read(self):
        self.read_path = askdirectory()
        self.lineEdit_read_add.setText(self.read_path + '/')

    def add_save(self):
        self.save_path = askdirectory()
        self.lineEdit_save_add.setText(self.save_path + '/')

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

        h1.set_sys_param(pixel_x = 1.85, pixel_y = 1.85, refractive_index = 1.52, \
                        magnification = 10, wavelength = 0.640)
        h1.get_sys_param()
        
    def param_set_confirm(self):
        self.close()

    def param_set_cancel(self):
        self.close()


# def TDHM_loop():
# code here...

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)  # Create an instance of QtWidgets.QApplication
    # apply_stylesheet(app, theme='dark_teal.xml')
    # app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())

    File = open('./ui_files/styles/Yiplab.qss', 'r')
    with File:
        qss_style = File.read()
        app.setStyleSheet(qss_style)

    h1 = dhm.core.HoloGram()

    launcher = Launcher()  # Create an instance of our class
    launcher.show()

    sys.exit(app.exec())
