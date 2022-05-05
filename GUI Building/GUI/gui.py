#!/usr/bin/env python3

import os.path
import sys

# import dhm.core
# import dhm.interactive
# import dhm.utils

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

        self.SysCalibration = SysCalib()
        self.Parameter = ParamSet()

        self.pushButton_calibration.clicked.connect(self.SysCalibration.show)
        self.pushButton_parameter.clicked.connect(self.Parameter.show)


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

    def param_set_confirm(self):
        #TdhmWidgetStd.checkBox_system.setChecked(True)
        # Here we should use "signal" to realize it. After clicking 'confirm', the coresponding checkbox in TdhmWidgetStd should be checked
        self.close()

    def param_set_cancel(self):
        self.close()


# def PrintButtonPressed(self):
#     # This is executed when the button is pressed
#     print('Input text:' + self.input.text())


# syscalib = SysCalib()
# paramset = ParamSet()
# tdhm_widget = TdhmWidgetStd()


#def TDHM_loop():
    # code here...

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)  # Create an instance of QtWidgets.QApplication
    #apply_stylesheet(app, theme='dark_teal.xml')
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    '''
    File = open('./ui_files/styles/Obit.qss', 'r')
    with File:
        qss_style = File.read()
        app.setStyleSheet(qss_style)
    '''
    launcher = Launcher()  # Create an instance of our class
    launcher.show()

    sys.exit(app.exec())
