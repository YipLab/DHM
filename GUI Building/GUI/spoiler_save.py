from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtGui import *
from PyQt5.QtCore import *


class Spoiler(QWidget):
    def __init__(self, parent=None, title='', animationDuration=300, addRemoveOption='None'):
        super(Spoiler, self).__init__(parent=parent)
        uic.loadUi('./ui_files/spoiler_widget.ui', self)  # Load the .ui file

        self.animationDuration = animationDuration
        self.toggleAnimation = QParallelAnimationGroup()
        # self.contentArea = QScrollArea()
        # self.headerLine = QFrame()
        # self.toggleButton = QToolButton()
        # self.mainLayout = QGridLayout()
        # self.childWidgets = []

        self.toggleButton.setStyleSheet("QToolButton { border: none; }")
        self.toggleButton.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.toggleButton.setArrowType(Qt.RightArrow)
        self.toggleButton.setText(str(title))
        self.toggleButton.setCheckable(True)
        self.toggleButton.setChecked(False)

        self.addRemoveOperation = addRemoveOption

        self.contentArea.setStyleSheet("QScrollArea { background-color: white; border: none; }")
        # self.contentArea.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
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
        # if addRemoveOption is not 'None':
        #     self.mainLayout.addWidget(self.addRemoveButton, 0, 2, 1, 1, Qt.AlignRight)
        # self.mainLayout.addWidget(self.contentArea, 1, 0, 1, 3)
        self.setLayout(self.mainLayout)

        def start_animation(checked):
            arrow_type = Qt.DownArrow if checked else Qt.RightArrow
            direction = QAbstractAnimation.Forward if checked else QAbstractAnimation.Backward
            self.toggleButton.setArrowType(arrow_type)
            self.toggleAnimation.setDirection(direction)
            self.toggleAnimation.start()

        self.toggleButton.clicked.connect(start_animation)
        self.pushButton_Confirm.clicked.connect(start_animation)
        # self.contentLayout = QVBoxLayout()
        # print (self.sizeHint())
        # print (self.contentLayout.sizeHint())
        # self.contentArea.setMaximumHeight(300 if self.contentLayout.sizeHint().height() < 300 else self.contentLayout.sizeHint().height())
        self.setContentLayout(self.contentLayout)


    def setContentLayout(self, contentLayout):
        self.contentArea.destroy()
        self.contentArea.setLayout(contentLayout)
        # print (self.sizeHint())
        collapsedHeight = self.sizeHint().height() - self.contentArea.maximumHeight()
        # contentHeight = 400 if contentLayout.sizeHint().height() > 400 else contentLayout.sizeHint().height()
        contentHeight = contentLayout.sizeHint().height()
        # print (contentLayout.sizeHint())
        for i in range(self.toggleAnimation.animationCount()-1):
            spoilerAnimation = self.toggleAnimation.animationAt(i)
            spoilerAnimation.setDuration(self.animationDuration)
            spoilerAnimation.setStartValue(collapsedHeight)
            spoilerAnimation.setEndValue(collapsedHeight + contentHeight)
        contentAnimation = self.toggleAnimation.animationAt(self.toggleAnimation.animationCount() - 1)
        contentAnimation.setDuration(self.animationDuration)
        contentAnimation.setStartValue(0)
        contentAnimation.setEndValue(contentHeight)


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        # uic.loadUi('./ui_files/std_main_alpha.ui', self)  # Load the .ui file
        self.init_ui()

    def init_ui(self):

        self.setGeometry(300, 300, 300, 220)
        self.setWindowIcon(QIcon('web.png'))

        self.scroll = QScrollArea()             # Scroll Area which contains the widgets, set as the centralWidget
        self.widget = QWidget()                 # Widget that contains the collection of Vertical Box
        self.vbox = QVBoxLayout()

        # for i in range(1,5):
        #     obj = QLabel("TextLabel")
        #     self.vbox.addWidget(obj)
        #     spoiler1 = Spoiler(addRemoveOption='None', title='Group 1')
        #     self.vbox.addWidget(spoiler1)

        self.spoiler1 = Spoiler(addRemoveOption='None', title='Group 1')
        self.spoiler2 = Spoiler(addRemoveOption='None', title='Group 2')
        self.spoiler3 = Spoiler(addRemoveOption='None', title='Group 3')
        self.vbox.addWidget(self.spoiler1)
        self.vbox.addWidget(self.spoiler2)
        self.vbox.addWidget(self.spoiler3)


        self.widget.setLayout(self.vbox)
        # self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        # self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setWidgetResizable(True)
        self.scroll.setWidget(self.widget)

        self.setCentralWidget(self.scroll)

        # self.setGeometry(600, 100, 1000, 900)
        self.setWindowTitle('Scroll Area Demonstration')
        self.show()

        # self.centralLayout.addWidget(self.spoiler1)
        # self.centralLayout.addWidget(self.spoiler2)
        # self.centralLayout.addWidget(self.spoiler3)
        # self.setCentralWidget(self.centralWidget)
        # self.show()

import sys

if __name__ == '__main__':

    app = QApplication(sys.argv)
    ex = MainWindow()
    sys.exit(app.exec_())