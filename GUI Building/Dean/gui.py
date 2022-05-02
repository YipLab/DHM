#!/usr/bin/env python3

import os.path
import sys

# import dhm.core
# import dhm.interactive
# import dhm.utils

from PyQt5 import QtWidgets, uic

class Launcher(QtWidgets.QMainWindow):
	def __init__(self):
		super(Launcher, self).__init__() # Call the inherited classes __init__ method
		uic.loadUi('./ui_files/launcher_window.ui', self) # Load the .ui file

		self.printButton.setText('Text Changed')
		self.button = self.findChild(QtWidgets.QPushButton, 'printButton')

		self.show() # Show the GUI

class SysCalib(QtWidgets.QDialog):
	def __init__(self):
		super(SysCalib, self).__init__() # Call the inherited classes __init__ method
		uic.loadUi('./ui_files/sys_calib_dialog.ui', self) # Load the .ui file
		self.show() # Show the GUI

class ParamSet(QtWidgets.QDialog):
	def __init__(self):
		super(ParamSet, self).__init__() # Call the inherited classes __init__ method
		uic.loadUi('./ui_files/param_set_dialog.ui', self) # Load the .ui file

		self.button.clicked.connect(self.printButtonPressed) # Remember to pass the definition/method, not the return value!


        # Set the print button text to "Text Changed"
        self.printButton.setText('Text Changed')
        # This should not throw an error as `uic.loadUi` would have created `self.printButton`


		self.show()

def printButtonPressed(self):
	# This is executed when the button is pressed
	print('Input text:' + self.input.text())


class TdhmWidgetStd(QtWidgets.QWidget):
	def __init__(self):
		super(TdhmWidgetStd, self).__init__() # Call the inherited classes __init__ method
		uic.loadUi('./ui_files/tdhm_widget_std.ui', self) # Load the .ui file

		self.button = self.findChild(QtWidgets.QPushButton, 'printButton') # Find the button
		self.button.clicked.connect(self.printButtonPressed) # Remember to pass the definition/method, not the return value!

		self.show()

	def printButtonPressed(self):
		# This is executed when the button is pressed
		print('printButtonPressed')

app = QtWidgets.QApplication(sys.argv) # Create an instance of QtWidgets.QApplication
launcher = Launcher() # Create an instance of our class
syscalib = SysCalib()
paramset = ParamSet()
tdhm_widget = TdhmWidgetStd()

# app.exec_()


def mainloop():
    """Starts the main loop."""
    sys.exit(app.exec())
