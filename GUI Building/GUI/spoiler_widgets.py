from PyQt5 import uic
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

class Spoiler(QWidget):
    spoiler_next_step = pyqtSignal()
    def __init__(self, parent=None, ui_path = '', animationDuration=300):
        super(Spoiler, self).__init__(parent=parent)
        uic.loadUi(ui_path, self)  # Load the .ui file

        self.label_check.hide()
        self.label_done_text.hide()

        self.animationDuration = animationDuration
        self.toggleAnimation = QParallelAnimationGroup()

        self.toggleButton.setStyleSheet("QToolButton { border: none; }")
        self.toggleButton.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.toggleButton.setArrowType(Qt.RightArrow)
        self.toggleButton.setCheckable(True)
        self.toggleButton.setChecked(False)

        self.contentArea.setStyleSheet("QScrollArea { background-color: white; border: none; }")
        self.contentArea.setMaximumHeight(0)
        self.contentArea.setMinimumHeight(0)

        self.toggleAnimation.addAnimation(QPropertyAnimation(self, b"minimumHeight"))
        self.toggleAnimation.addAnimation(QPropertyAnimation(self, b"maximumHeight"))
        self.toggleAnimation.addAnimation(QPropertyAnimation(self.contentArea, b"maximumHeight"))

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
        self.pushButton_Confirm.clicked.connect(self.label_check.show)
        self.pushButton_Confirm.clicked.connect(self.label_done_text.show)
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

class load_img_Spoiler(Spoiler):
    def __init__(self, parent=None, ui_path = '', animationDuration=300):
        super(load_img_Spoiler, self).__init__(parent=parent, ui_path = ui_path, animationDuration=animationDuration)

class set_roi_Spoiler(Spoiler):
    def __init__(self, parent=None, ui_path = '', animationDuration=300):
        super(set_roi_Spoiler, self).__init__(parent=parent, ui_path = ui_path, animationDuration=animationDuration)

class set_save_Spoiler(Spoiler):
    def __init__(self, parent=None, ui_path = '', animationDuration=300):
        super(set_save_Spoiler, self).__init__(parent=parent, ui_path = ui_path, animationDuration=animationDuration)

class process_dhm_Spoiler(Spoiler):
    def __init__(self, parent=None, ui_path = '', animationDuration=300):
        super(process_dhm_Spoiler, self).__init__(parent=parent, ui_path = ui_path, animationDuration=animationDuration)
