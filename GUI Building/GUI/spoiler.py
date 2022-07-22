from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt
import sys

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

class Spoiler(QWidget):
    spoiler_next_step = pyqtSignal()
    def __init__(self, parent=None, ui_path = '', animationDuration=300):
        super(Spoiler, self).__init__(parent=parent)
        uic.loadUi(ui_path, self)  # Load the .ui file

        self.animationDuration = animationDuration
        self.toggleAnimation = QParallelAnimationGroup()

        self.toggleButton.setStyleSheet("QToolButton { border: none; }")
        self.toggleButton.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.toggleButton.setArrowType(Qt.RightArrow)
        self.toggleButton.setCheckable(True)
        self.toggleButton.setChecked(False)

        self.contentArea.setStyleSheet("QScrollArea { background-color: white; border: none; }")
        # start out collapsed
        self.contentArea.setMaximumHeight(0)
        self.contentArea.setMinimumHeight(0)
        # let the entire widget grow and shrink with its content
        self.toggleAnimation.addAnimation(QPropertyAnimation(self, b"minimumHeight"))
        self.toggleAnimation.addAnimation(QPropertyAnimation(self, b"maximumHeight"))
        self.toggleAnimation.addAnimation(QPropertyAnimation(self.contentArea, b"maximumHeight"))
        # don't waste space
        self.mainLayout.setVerticalSpacing(0)
        self.mainLayout.setContentsMargins(0, 0, 0, 0)
        self.mainLayout.addWidget(self.toggleButton, 0, 0, 1, 1, Qt.AlignLeft)
        self.setLayout(self.mainLayout)

        def start_animation(checked):
            arrow_type = Qt.DownArrow if checked else Qt.RightArrow
            direction = QAbstractAnimation.Forward if checked else QAbstractAnimation.Backward
            self.toggleButton.setArrowType(arrow_type)
            self.toggleAnimation.setDirection(direction)
            self.toggleAnimation.start()

        self.toggleButton.clicked.connect(start_animation)
        self.pushButton_Confirm.clicked.connect(self.spoiler_next_step)
        self.pushButton_Confirm.clicked.connect(self.toggleButton.click)
        self.setContentLayout(self.contentLayout)

    def drop_spoiler(self):
        self.toggleButton.click()

    def setContentLayout(self, contentLayout):
        self.contentArea.destroy()
        self.contentArea.setLayout(contentLayout)
        collapsedHeight = self.sizeHint().height() - self.contentArea.maximumHeight()
        contentHeight = contentLayout.sizeHint().height()

        for i in range(self.toggleAnimation.animationCount()-1):
            spoilerAnimation = self.toggleAnimation.animationAt(i)
            spoilerAnimation.setDuration(self.animationDuration)
            spoilerAnimation.setStartValue(collapsedHeight)
            spoilerAnimation.setEndValue(collapsedHeight + contentHeight)

        contentAnimation = self.toggleAnimation.animationAt(self.toggleAnimation.animationCount() - 1)
        contentAnimation.setDuration(self.animationDuration)
        contentAnimation.setStartValue(0)
        contentAnimation.setEndValue(contentHeight)

class set_param_Spoiler(Spoiler):
    def __init__(self, parent=None, ui_path = '', animationDuration=300):
        super(set_param_Spoiler, self).__init__(parent=parent, ui_path = ui_path, animationDuration=animationDuration)


class TDHMWidgetStd(QMainWindow):

    def __init__(self):
        super(TDHMWidgetStd, self).__init__()
        uic.loadUi('./ui_files/std_main_alpha.ui', self)  # Load the .ui file
        self.init_ui()

    def init_ui(self):

        self.img_canvas = FigureCanvas(plt.Figure())
        self.img_canvas.minimumWidth = 800
        self.img_canvas.minimumHeight = 600
        self.bar_layout.addWidget(NavigationToolbar(self.img_canvas, self))
        self.figure_layout.addWidget(self.img_canvas)

        self.spoiler1 = set_param_Spoiler(ui_path ='./ui_files/spoiler_param_set_widget.ui')
        self.spoiler2 = Spoiler(ui_path='./ui_files/spoiler_template_widget.ui')
        self.spoiler3 = Spoiler(ui_path='./ui_files/spoiler_template_widget.ui')
        self.vbox.addWidget(self.spoiler1)
        self.vbox.addWidget(self.spoiler2)
        self.vbox.addWidget(self.spoiler3)
        self.spoiler1.spoiler_next_step.connect(self.spoiler2.drop_spoiler)
        self.spoiler2.spoiler_next_step.connect(self.spoiler3.drop_spoiler)
        self.scroll.setWidgetResizable(True)
        self.scroll.setWidget(self.widget)

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