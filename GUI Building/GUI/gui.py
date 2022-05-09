#!/usr/bin/env python3
from PyQt5 import QtWidgets, uic
import os.path
import sys
from tkinter.filedialog import askdirectory
from dhm import coreFuctions
# import dhm.interactive
# import dhm.utils
import tifffile as tf
import random
import numpy as np

from matplotlib.backends.qt_compat import QtCore
from qt_material import apply_stylesheet
import qdarkstyle
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import matplotlib.pyplot as plt


class Launcher(QtWidgets.QMainWindow):
    def __init__(self):
        super(Launcher, self).__init__()  # Call the inherited classes __init__ method
        uic.loadUi('./ui_files/launcher_window.ui', self)  # Load the .ui file

        self.std_TDHM = TdhmWidgetStd()

        self.standard_TDHM.clicked.connect(self.std_TDHM.show)


class TdhmWidgetStd(QtWidgets.QMainWindow):
    def __init__(self):
        super(TdhmWidgetStd, self).__init__()  # Call the inherited classes __init__ method
        uic.loadUi('./ui_files/std_main.ui', self)  # Load the .ui file

        self.img_canvas = FigureCanvas(plt.Figure())
        self.img_canvas.minimumWidth = 800
        self.img_canvas.minimumHeight = 600
        self.Bar_layout.addWidget(NavigationToolbar(self.img_canvas, self))

        self.figure_layout.addWidget(self.img_canvas)

        self.save_path = None
        self.read_path = None
        self.hologram = None
        self.background = None

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

        self.pushButton_start.clicked.connect(self.start)

        self.image_figure = self.img_canvas.figure.subplots()

        self.num = 1

    def start(self):
        DHM_core.set_read_path(read_path=self.lineEdit_read_add.text())
        DHM_core.set_background_img(bgd_file_name=str(self.num))
        self.image_figure.imshow(DHM_core.BACKGROUND, cmap='gist_gray')
        self.img_canvas.draw()
        self.num += 1

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
            self.pushButton_start.setText('Next Frame')
        else:
            self.pushButton_read_add.show()
            self.label_read_add.show()
            self.lineEdit_read_add.show()
            self.pushButton_start.setText('Start')


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
        DHM_core.set_sys_param(pixel_x=self.pixel_size.value(),
                               pixel_y=self.pixel_size.value(),
                               refractive_index=self.refractive_index.value(),
                               magnification=self.magnification.value(),
                               wavelength=self.wave_length.value())
        DHM_core.set_expansion(expansion=self.expansion.value())
        DHM_core.set_recon_param(recon_enable=self.checkBox_recon.isChecked(),
                                 rec_start=self.SpinBox_start_recon.value(),
                                 rec_end=self.SpinBox_end_recon.value(),
                                 rec_step=self.SpinBox_step_recon.value(),
                                 detect_method=self.detected_method.currentText())

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

    DHM_core = coreFuctions.HoloGram()

    # image_show = tf.imread('./ui_files/icons' + '/0.tiff')
    # image_show = np.array(image_show[:, :], dtype=float)

    launcher = Launcher()  # Create an instance of our class
    launcher.show()

    sys.exit(app.exec())
