#!/usr/bin/env python3
from PyQt5 import QtWidgets, uic
from qrangeslider import QRangeSlider
import sys
from tkinter.filedialog import askdirectory, askopenfilename
import dhm.core
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.widgets import RectangleSelector
import matplotlib.pyplot as plt
import numpy as np
import time
import os


class Launcher(QtWidgets.QMainWindow):
    def __init__(self):
        super(Launcher, self).__init__()  # Call the inherited classes __init__ method
        uic.loadUi('./ui_files/launcher_window.ui', self)  # Load the .ui file

        self.standardTDHM = TDHMWidgetStd()

        self.standard_TDHM.clicked.connect(self.standardTDHM.show)


class TDHMWidgetStd(QtWidgets.QMainWindow):
    def __init__(self):
        super(TDHMWidgetStd, self).__init__()  # Call the inherited classes __init__ method
        uic.loadUi('./ui_files/std_main.ui', self)  # Load the .ui file

        self.textBrowser_info_show.setText('Standard Operation Procedure Setting ...\n   Step 1: Parameter Setting...')
        self.img_canvas = FigureCanvas(plt.Figure())
        self.img_canvas.minimumWidth = 800
        self.img_canvas.minimumHeight = 600

        # self.rangeSlider1 = QRangeSlider()

        # self.rangeSlider1.setRange(0, 100)
        # self.rangeSlider1.setBackgroundStyle('background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #222, stop:1 #333);')
        # self.rangeSlider1.setSpanStyle('background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #282, stop:1 #393);')

        self.Bar_layout.addWidget(NavigationToolbar(self.img_canvas, self))
        self.figure_layout.addWidget(self.img_canvas)
        # self.rangeSlider_layout.addWidget(self.rangeSlider1)

        self.hologram = None
        self.background = None

        self.pushButton_start.hide()
        self.label_calibration.setHidden(True)
        self.pushButton_calibration.hide()
        self.pushButton_background.hide()
        self.label_background.setHidden(True)
        self.label_parameter.setHidden(True)
        self.parameter_setting_check()
        self.pushButton_ImgSave.hide()
        self.comboBox_imgshow.hide()
        self.label_imgshow.setHidden(True)
        # self.rangeSlider1.show()

        # Ui Loading ###################
        self.SysCalibration = SysCalib()
        self.Parameter = ParamSet()
        self.Background = BackgroundSet()

        self.pushButton_calibration.clicked.connect(self.sys_calibration)
        self.pushButton_parameter.clicked.connect(self.parameter_set)
        self.pushButton_background.clicked.connect(self.background_set)

        # Push Button Connection #############
        # self.radioButton_liveimg.toggled.connect(self.live_image_check)
        self.pushButton_refresh.clicked.connect(self.parameter_setting_check)
        self.pushButton_ImgSave.clicked.connect(self.img_save)
        self.comboBox_imgshow.currentIndexChanged.connect(self.what_to_show)

        # Main Function Start ##############
        self.pushButton_start.clicked.connect(self.start)

        self.image_figure = self.img_canvas.figure.subplots()
        self.image_figure_ax = self.img_canvas.figure.gca()

    def start(self):
        self.pushButton_start.setStyleSheet("font: 20pt 'Arial Black';")

        # TODO: the textBrowser is not showing correctly...

        self.textBrowser_info_show.setText('Hologram Reading ... ')
        DHM.add_hologram_img(DHM.HOLO_NAME)

        self.textBrowser_info_show.append('Background and FFT Filter Creating... ')
        DHM.filter_background_process()

        self.textBrowser_info_show.append('Hologram Processing... ')

        DHM.hologram_process()

        # save
        self.image_show(DHM.HEIGHT_MAP)
        # self.image_show(DHM.PHASE_MAP)
        # self.image_show(DHM.WRAPPED_PHASE)

        self.pushButton_ImgSave.show()
        self.comboBox_imgshow.show()
        self.label_imgshow.setHidden(False)

        # DHM.save_results(self.num)
        # self.Note.addText("Current image saved.")

    def image_show(self, img_name):
        self.image_figure.imshow(img_name, cmap='gist_gray')
        self.img_canvas.draw()

    def img_save(self):
        self.textBrowser_info_show.append('Image saving... ')
        path = askdirectory()
        if not os.path.exists(path):
            os.makedirs(path)
        DHM.image_save(path_to_save=path, name=DHM.HOLO_NAME)

    def what_to_show(self):
        img_show = DHM.set_img_show(self.comboBox_imgshow.currentText())
        self.image_show(img_show)

    def sop_check(self):
        if (self.label_parameter.text() == 'Done') and (self.label_background.text() == 'Done'):
            if self.label_calibration.text() == 'Done':
                self.textBrowser_info_show.setText("Click the 'Next Frame' button to show the next result frame")
                self.pushButton_start.show()
            elif not self.radioButton_liveimg.isChecked():
                self.textBrowser_info_show.setText('All set!!! \n You can start processing now..')
                self.pushButton_start.show()
            else:
                self.pushButton_start.hide()
        else:
            self.pushButton_start.hide()

    def sys_calibration(self):
        self.SysCalibration.show()
        self.label_calibration.setText('Done')
        self.label_calibration.setHidden(False)
        self.pushButton_calibration.setStyleSheet("font: 10pt 'Arial Black';")
        self.sop_check()

    def parameter_set(self):
        self.Parameter.show()
        self.label_parameter.setText('Done')
        self.label_parameter.setHidden(False)
        self.pushButton_parameter.setStyleSheet("font: 10pt 'Arial Black';")
        self.sop_check()
        self.instruction.setText('SOP Instruction:\n      Step 2: Background and ROI Setting...')
        self.pushButton_background.show()

    def background_set(self):
        self.Background.show()
        self.label_background.setText('Done')
        self.label_background.setHidden(False)
        self.pushButton_background.setStyleSheet("font: 10pt 'Arial Black';")
        self.sop_check()

    def parameter_setting_check(self):
        # Configure Parameters ##############
        self.label_pixel.setText(str('%.2f' % DHM.pixel_x_main) + 'um')
        self.label_RI.setText(str('%.2f' % DHM.refractive_index_main))
        self.label_mag.setText(str('%.0f' % DHM.magnification_main) + 'x')
        self.label_wavelenth.setText(str('%.0f' % (DHM.wavelength_main * 1000)) + 'nm')

        # Reconstruction Parameters ###############
        if DHM.recon_enable_main:
            self.label_enable.setText(str(DHM.recon_enable_main))
            self.label_start.setText(str(DHM.rec_start_main))
            self.label_end.setText(str(DHM.rec_end_main))
            self.label_step.setText(str(DHM.rec_step_main))
            self.label_sharpness.setText(str(DHM.detect_method_main))
            self.label_start.setHidden(False)
            self.label_end.setHidden(False)
            self.label_step.setHidden(False)
            self.label_sharpness.setHidden(False)
        else:
            self.label_enable.setText(str(DHM.recon_enable_main))
            self.label_start.setHidden(True)
            self.label_end.setHidden(True)
            self.label_step.setHidden(True)
            self.label_sharpness.setHidden(True)

        # Process Setting ###############
        self.label_leveling.setText(str(DHM.leveling_method_main))
        self.label_holo_total.setText(str(DHM.holo_total_main))
        self.label_holo_strat.setText(str(DHM.holo_start_main))
        self.label_roi_enable.setText(str(DHM.ROI_enable))
        if DHM.leveling_method_main == "Gaussian Blur":
            self.label_Gaussian_size.setHidden(False)
            self.label_GB_size.setHidden(False)
            self.label_Gaussian_size.setText(str(DHM.gaussian_size_main))
        else:
            self.label_Gaussian_size.setHidden(True)
            self.label_GB_size.setHidden(True)

        # FFT Filter Setting
        self.label_FFT_filter.setText(DHM.filter_type_main)
        self.label_filter_rate.setText(str(DHM.filter_rate_main))
        self.label_quadrant.setText(str(DHM.filter_quadrant_main))
        self.label_expansion.setText(str(DHM.expansion_main))

        # What to Save
        self.label_Height.setText(str(DHM.height_map_main))
        self.label_Phase.setText(str(DHM.phase_map_main))
        self.label_Wrapped_phase.setText(str(DHM.wrapped_phase_main))
        self.label_refocused_volume.setText(str(DHM.refocused_volume_main))

    def live_image_check(self):
        if self.radioButton_liveimg.isChecked():
            self.pushButton_read_add.hide()
            self.pushButton_calibration.show()
            self.label_read_add.hide()
            self.lineEdit_read_add.hide()
            self.pushButton_start.setText('Next Frame')
        else:
            self.pushButton_read_add.show()
            self.label_read_add.show()
            self.lineEdit_read_add.show()
            self.label_calibration.setHidden(True)
            self.pushButton_calibration.hide()
            self.pushButton_start.setText('Start')
        self.sop_check()


class BackgroundSet(QtWidgets.QMainWindow):
    def __init__(self):
        super(BackgroundSet, self).__init__()  # Call the inherited classes __init__ method
        uic.loadUi('./ui_files/background_set_dialog.ui', self)  # Load the .ui file

        self.ROI_set.hide()

        self.save_path = None
        self.read_path = None
        self.background_save_address = None
        self.background_read_address = None

        self.img_canvas_back = FigureCanvas(plt.Figure())
        self.img_canvas_back.minimumWidth = 800
        self.img_canvas_back.minimumHeight = 600
        self.Layout_tool.addWidget(NavigationToolbar(self.img_canvas_back, self))

        self.Layout_frame.addWidget(self.img_canvas_back)
        self.image_figure_back = self.img_canvas_back.figure.subplots()
        self.image_figure_ax = self.img_canvas_back.figure.gca()

        self.background_method()
        self.comboBox_background_method.currentTextChanged.connect(self.background_method)
        self.pushButton_cam_save.clicked.connect(self.background_save)
        self.pushButton_local_read.clicked.connect(self.background_read)
        self.pushButton_confirm.clicked.connect(self.back_confirm)
        self.pushButton_cancel.clicked.connect(self.back_cancel)
        self.checkBox_ROI_set.stateChanged.connect(self.roi_set)
#=========Do Sth here========#

        self.pushButton_read_add.clicked.connect(self.add_read)
        self.pushButton_save_add.clicked.connect(self.add_save)

        self.lineEdit_holo_name.textChanged.connect(self.holo_name)

        # self.label_save_add.setHidden(True)
        # self.lineEdit_save_add.hide()
        # self.pushButton_save_add.hide()


        # self.verticalWidget_back.hide()

    def roi_set(self):

        def roi_set_line_select_callback(eclick, erelease):
            'eclick and erelease are the press and release events'
            x1, y1 = eclick.xdata, eclick.ydata
            x2, y2 = erelease.xdata, erelease.ydata
            print("(%3.2f, %3.2f) --> (%3.2f, %3.2f)" % (x1, y1, x2, y2))
            # print(" The button you used were: %s %s" % (eclick.button, erelease.button))

        def roi_set_toggle_selector(event):
            print("Selector Launched.")
            # print(' Key pressed.')
            # if event.key in ['Q', 'q'] and toggle_selector.RS.active:
            #     print(' RectangleSelector deactivated.')
            #     toggle_selector.RS.set_active(False)
            # if event.key in ['A', 'a'] and not toggle_selector.RS.active:
            #     print(' RectangleSelector activated.')
            #     toggle_selector.RS.set_active(True)

        self.image_figure_back.imshow(DHM.HOLOGRAM, cmap='gist_gray')
        self.img_canvas_back.draw()
        print("\n      click  -->  release")

        # drawtype is 'box' or 'line' or 'none'
        roi_set_toggle_selector.RS = RectangleSelector(self.image_figure_ax, roi_set_line_select_callback,
                                               drawtype='box', useblit=True,
                                               button=[1, 3],  # don't use middle button
                                               minspanx=5, minspany=5,
                                               spancoords='pixels',
                                               interactive=True)
        plt.connect('key_press_event', roi_set_toggle_selector)
        # plt.show()
        self.img_canvas_back.draw_idle()

        if self.checkBox_ROI_set.isChecked():
            self.ROI_set.show()
        else:
            self.ROI_set.hide()

    def back_confirm(self):
        DHM.set_roi_para(roi_enable=self.checkBox_ROI_set.isChecked())
        self.close()

    def back_cancel(self):
        self.close()

    def background_save(self):
        self.background_save_address = askdirectory()
        self.lineEdit_cam_save.setText(self.background_save_address + '/')

    def background_read(self):
        # self.background_read_address = askopenfilename()
        self.background_read_address = "../../Example Images/ref.tiff"
        DHM.set_background_img(read_path_back=self.background_read_address)
        self.lineEdit_local_read.setText(self.background_read_address)
        self.Note.setText(self.background_read_address)
        self.Note.append(f"Background is set, resolution is ({DHM.shape_x_main},{DHM.shape_y_main})")

        self.image_figure_back.imshow(DHM.BACKGROUND, cmap='gist_gray')
        self.img_canvas_back.draw()

    def add_read(self):
        # self.read_path = askdirectory()
        # self.lineEdit_read_add.setText(self.read_path + '/')
        self.read_path = "../../Example Images/"
        self.lineEdit_read_add.setText(self.read_path)
        DHM.set_read_path(read_path=self.lineEdit_read_add.text())
        DHM.add_hologram_img('1')
        if DHM.auto_save:
            self.lineEdit_save_add.show()
            self.pushButton_save_add.show()
            self.label_save_add.setHidden(False)
        else:
            self.lineEdit_save_add.hide()
            self.pushButton_save_add.hide()
            self.label_save_add.setHidden(True)
            self.verticalWidget_back.show()

    def add_save(self):
        self.save_path = "../../Example Images/"
        self.lineEdit_save_add.setText(self.save_path)
        DHM.set_save_path(save_path=str(self.lineEdit_save_add.text()))
        self.verticalWidget_back.show()

    def holo_name(self):
        DHM.HOLO_NAME = self.lineEdit_holo_name.text()


    def background_method(self):
        if self.comboBox_background_method.currentText() == "Local":
            self.label_cam_back.setHidden(True)
            self.label_cam_save.setHidden(True)
            self.lineEdit_cam_save.hide()
            self.pushButton_cam_save.hide()
            self.pushButton_cam_open.hide()
            self.pushButton_cam_save_back.hide()
            self.label_local.setHidden(False)
            self.label_local_read.setHidden(False)
            self.lineEdit_local_read.show()
            self.pushButton_local_read.show()
        else:
            self.label_cam_back.setHidden(False)
            self.label_cam_save.setHidden(False)
            self.lineEdit_cam_save.show()
            self.pushButton_cam_save.show()
            self.pushButton_cam_open.show()
            self.pushButton_cam_save_back.show()
            self.label_local.setHidden(True)
            self.label_local_read.setHidden(True)
            self.lineEdit_local_read.hide()
            self.pushButton_local_read.hide()


class SysCalib(QtWidgets.QDialog):
    def __init__(self):
        super(SysCalib, self).__init__()  # Call the inherited classes __init__ method
        uic.loadUi('./ui_files/sys_calib_dialog.ui', self)  # Load the .ui file


class ParamSet(QtWidgets.QDialog):
    def __init__(self):
        super(ParamSet, self).__init__()  # Call the inherited classes __init__ method
        uic.loadUi('./ui_files/param_set_dialog.ui', self)  # Load the .ui file

        self.label_start_recon.setHidden(True)
        self.label_end_recon.setHidden(True)
        self.label_step_recon.setHidden(True)
        self.label_sharp_detect.setHidden(True)
        self.SpinBox_start_recon.hide()
        self.SpinBox_end_recon.hide()
        self.SpinBox_step_recon.hide()
        self.detected_method.hide()

        self.pushButton_confirm.clicked.connect(self.param_set_confirm)
        self.pushButton_cancel.clicked.connect(self.param_set_cancel)
        self.checkBox_recon_enable.stateChanged.connect(self.recon_enable)

    def recon_enable(self):
        if self.checkBox_recon_enable.isChecked():
            self.label_start_recon.setHidden(False)
            self.label_end_recon.setHidden(False)
            self.label_step_recon.setHidden(False)
            self.label_sharp_detect.setHidden(False)
            self.SpinBox_start_recon.show()
            self.SpinBox_end_recon.show()
            self.SpinBox_step_recon.show()
            self.detected_method.show()
        else:
            self.label_start_recon.setHidden(True)
            self.label_end_recon.setHidden(True)
            self.label_step_recon.setHidden(True)
            self.label_sharp_detect.setHidden(True)
            self.SpinBox_start_recon.hide()
            self.SpinBox_end_recon.hide()
            self.SpinBox_step_recon.hide()
            self.detected_method.hide()

    def param_set_confirm(self):
        DHM.set_sys_param(pixel_x=self.pixel_size.value(),
                          pixel_y=self.pixel_size.value(),
                          refractive_index=self.refractive_index.value(),
                          magnification=self.magnification.value(),
                          wavelength=self.wave_length.value())

        DHM.set_filter_para(expansion=self.expansion.value(),
                            filter_type=self.comboBox_FilterType.currentText(),
                            filter_rate=self.doubleSpinBox_rate.value(),
                            filter_quadrant=self.comboBox_quadrant.currentText())

        DHM.set_what_to_save(height_map=self.checkBox_height.isChecked(),
                             phase_map=self.checkBox_phase.isChecked(),
                             wrapped_phase=self.checkBox_wrapped_phase.isChecked(),
                             refocused_volume=self.checkBox_refocus_volume.isChecked(),
                             auto_save=self.checkBox_auto_save.isChecked())

        DHM.set_processing_para(leveling_method=self.comboBox_leveling.currentText(),
                                gaussian_size=self.doubleSpinBox_gaussian_size.value(),
                                holo_count=self.doubleSpinBox_holo_count.value(),
                                holo_start=self.doubleSpinBox_holo_start.value())

        DHM.set_recon_param(recon_enable=self.checkBox_recon_enable.isChecked(),
                            rec_start=self.SpinBox_start_recon.value(),
                            rec_end=self.SpinBox_end_recon.value(),
                            rec_step=self.SpinBox_step_recon.value(),
                            detect_method=self.detected_method.currentText())

        self.close()

    def param_set_cancel(self):
        self.close()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)  # Create an instance of QtWidgets.QApplication
    # apply_stylesheet(app, theme='dark_teal.xml')
    # app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())

    File = open('./ui_files/styles/Yip_lab.qss', 'r')
    with File:
        qss_style = File.read()
        app.setStyleSheet(qss_style)

    DHM = dhm.core.HoloGram()

    launcher = Launcher()  # Create an instance of our class
    launcher.show()

    sys.exit(app.exec())
