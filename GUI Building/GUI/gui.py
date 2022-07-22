#!/usr/bin/env python3
import os, sys, time, multiprocessing as mp

from PyQt5 import uic
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QFont
from PyQt5.QtCore import *
from spoiler_widgets import *
import easygui as esg

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas, NavigationToolbar2QT as NavigationToolbar

import matplotlib.pyplot as plt, matplotlib.patches as patches
from matplotlib.widgets import RectangleSelector

import numpy as np
import dhm.core

q_mutex = QMutex()

class UiManager:
    def __init__(self):
        self.launcher = Launcher()
        self.standardTDHM = TDHMWidgetStd()
        self.launcher.launcher_hide.connect(self.standardTDHM.show)
        # self.standardTDHM.launcher_show.connect(self.launcher.show)
        self.launcher.show()

class Launcher(QMainWindow):
    launcher_hide = pyqtSignal()
    def __init__(self):
        super(Launcher, self).__init__()  # Call the inherited classes __init__ method
        uic.loadUi('./ui_files/launcher_window.ui', self)  # Load the .ui file

        self.standard_TDHM.clicked.connect(self.hide)
        self.standard_TDHM.clicked.connect(self.launcher_hide)

class TDHMWidgetStd(QMainWindow):

    def __init__(self):
        super(TDHMWidgetStd, self).__init__()
        uic.loadUi('./ui_files/std_main_alpha.ui', self)  # Load the .ui file
        self.init_ui()

    def init_ui(self):

        self.text_info_show.setText("")
        self.img_canvas = FigureCanvas(plt.Figure())
        self.img_canvas.minimumWidth = 800
        self.img_canvas.minimumHeight = 600
        self.bar_layout.addWidget(NavigationToolbar(self.img_canvas, self))
        self.figure_layout.addWidget(self.img_canvas)
        self.image_figure = self.img_canvas.figure.subplots()
        self.image_figure_ax = self.img_canvas.figure.gca()

        self.spoiler1 = set_param_Spoiler(ui_path ='./ui_files/spoiler_set_param_widget.ui')
        self.spoiler2 = load_img_Spoiler(ui_path='./ui_files/spoiler_load_img_widget.ui')
        self.spoiler3 = set_roi_Spoiler(ui_path='./ui_files/spoiler_set_roi_widget.ui')
        self.spoiler4 = set_save_Spoiler(ui_path='./ui_files/spoiler_set_save_widget.ui')
        self.spoiler5 = process_dhm_Spoiler(ui_path='./ui_files/spoiler_process_dhm_widget.ui')

        self.vbox.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        self.vbox.addWidget(self.spoiler1)
        self.vbox.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        self.vbox.addWidget(self.spoiler2)
        self.vbox.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        self.vbox.addWidget(self.spoiler3)
        self.vbox.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        self.vbox.addWidget(self.spoiler4)
        self.vbox.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        self.vbox.addWidget(self.spoiler5)
        self.vbox.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

        self.spoiler1.spoiler_next_step.connect(self.spoiler2.drop_spoiler)
        self.spoiler2.spoiler_next_step.connect(self.spoiler3.drop_spoiler)
        self.spoiler3.spoiler_next_step.connect(self.spoiler4.drop_spoiler)
        self.spoiler4.spoiler_next_step.connect(self.spoiler5.drop_spoiler)
        self.scroll.setWidgetResizable(True)
        self.scroll.setWidget(self.widget)

        self.progressBar.hide()
        self.pushButton_end_task.hide()
        self.pushButton_start_pause.hide()

        self.pushButton_view_img.setEnabled(False)
        self.spinBox_select_img.setEnabled(False)


if __name__ == '__main__':

    app = QApplication(sys.argv)
    app.setFont(QFont('Helvetica Neue'))
    app.setStyleSheet("QLabel{font-family: 'Helvetica';}")
    # File = open('./ui_files/styles/Yip_lab.qss', 'r')
    # with File:
    #     qss_style = File.read()
    #     app.setStyleSheet(qss_style)

    ui_manager = UiManager()
    sys.exit(app.exec_())