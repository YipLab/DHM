# #####################################################################################################################
# This program is for digital holographic microscope
# Main Idea:
#            Auto-Focusing with Angular Spectrum (Fourier sharpness);
#            Auto-Fourier Filtering;
#            Phase unwrapping
#
# Camera Info: FLIR BFS-U3-120S4M-CS, Pixel size: 1.85um, (4000 x 3000)
#
# Date: 2022-Jan-12
# #####################################################################################################################

##DHM_core

import numpy as np
from tkinter.filedialog import askdirectory
import tifffile as tf
from tqdm import tqdm
import matplotlib.pyplot as plt
import math
import pandas as pd
from skimage.filters import gaussian
from skimage.restoration import unwrap_phase  # intall 'Microsoft's vcredist_x64.exe' if it not work 
# ( https://docs.microsoft.com/en-us/cpp/windows/latest-supported-vc-redist?view=msvc-170) 
import openpyxl
from typing import Optional, Tuple, List, Any

class HoloGram:

	_COMPLEX_J = complex(0, 1)
	_SHAR = []
	
	def __init__(self, hologram, background):
		self.hologram = hologram
		self._background = background
		# customized parameter
		self._expansion = 100

		# System Parameter
		self._pixel_x = 1.85
		self._pixel_y = 1.85  # micro-meter (unit)
		self._diffraction_index = 1.52
		self._magnification = 10
		self._wavelength = 0.640  # 640nm

		self._shape_x = hologram.shape[0]
		self._shape_y = hologram.shape[1]

		self.vector = 2 * self.diffraction_index * np.pi / self.wavelength
		self.delta = self.pixel_x / self.magnification

		self.left = None
		self.right = None
		self.top = None
		self.bot = None

	def set_hologram_img(self, hologram):
		
		if (hologram.shape() != self.hologram.shape()):
			self.left = None
			self.right = None
			self.top = None
			self.bot = None

			print ("Hologram image size changed, ROI is reset")

		self.hologram = hologram
		self._shape_x = hologram.shape[0]
		self._shape_y = hologram.shape[1]

	def set_sys_param(self, pixel_x:float = 1.85, pixel_y:float = 1.85, diffraction_index:float = 1.52,\
			magnification:int = 10, wavelength:float = 0.640):
		self._pixel_x = pixel_x
		self._pixel_y = pixel_y  # micro-meter (unit)
		self._diffraction_index = diffraction_index
		self._magnification = magnification
		self._wavelength = wavelength  # 640nm

		self.vector = 2 * self.diffraction_index * np.pi / self.wavelength
		self.delta = self.pixel_x / self.magnification

	def get_sys_param(self)-> Tuple[Optional[float], Optional[float], Optional[float], Optional[int], Optional[float]]:
		print  ("pixel_x = "+self._pixel_x+"um\n"\
				"pixel_y = "+self._pixel_y+"um\n"\
				"diffraction_index = "+self._diffraction_index+"\n"\
				"magnification = "+self._magnification+"\n"\
				"wavelength = "+self._wavelength+"nm\n"\
				)
		return self._pixel_x, self._pixel_y, self._diffraction_index, self._magnification, self._wavelength

	def set_expansion(self, expansion:int = 100): 
		self.expansion = expansion
	
	def get_expansion(self, expansion:int = 100) -> Optional[int]:
		print ("expansion factor = "+self.expansion+"\n")
		return self.expansion

	def holo_roi_show(self):
		print ("Currently viewing ROI: (left, right, top, bottom) = ("+self.left+", "+self.right+", "+self.top+", "+self.bot+"),\n"\
			"Whole image size is: ("+self._shape_x+", "self._shape_y+")")
		plt.imshow(self.hologram[self.left: self.right, self.top: self.bot], cmap='gray')  # 8-bit grey scale
    	plt.ginput(1)

    def holo_show(self):
		print ("Currently viewing the whole image, image size is: ("+self._shape_x+", "self._shape_y+")")
		plt.imshow(self.hologram, cmap='gray')  # 8-bit grey scale
    	plt.ginput(1)

    def set_roi_by_centre(self, radius:int = 200):
    	print ("Currently viewing the whole image, image size is: ("+self._shape_x+", "self._shape_y+")")
    	print ("Set ROI by Centre: Click to set the centre of ROI with a raidus of :"+radius)
    	plt.imshow(self.hologram, cmap='gray')  # 8-bit grey scale
    	roi_x = plt.ginput(1)
    	self.top = np.int(np.subtract(roi_x[0][0], radius))
    	self.bot = np.int(np.add(roi_x[0][0], radius))
    	self.left = np.int(np.subtract(roi_x[0][1], radius))
    	self.right = np.int(np.add(roi_x[0][1], radius))
    	print ("ROI updated to: (left, right, top, bottom)= ("+self.left+", "+self.right+", "+self.top+", "+self.bot+"),\n")

	def set_roi_by_corner(self):
    	print ("Currently viewing the whole image, image size is: ("+self._shape_x+", "self._shape_y+")")
    	print ("Set ROI by Corner: Click the desired top left and bottom right corner to set ROI coordinates")
    	plt.imshow(self.hologram, cmap='gray')  # 8-bit grey scale
	    roi_x, roi_y = plt.ginput(2)

	    top = int(roi_x[0])
	    bot = int(roi_y[0])
	    left = int(roi_x[1])
	    right = int(roi_y[1])

	    if (top - bot) % 2 != 0:
	        bot = bot - 1
	    if (left - right) % 2 != 0:
	        right = right - 1

	    self.top = top
    	self.bot = bot
    	self.left = left
    	self.right = right
    	print ("ROI updated to: (left, right, top, bottom)= ("+self.left+", "+self.right+", "+self.top+", "+self.bot+"),\n")


	def set_roi_by_param(self, left:int, right:int, top:int, bottom:int):
		self.top = top
    	self.bot = bottom
    	self.left = left
    	self.right = right
		print ("ROI set to: (left, right, top, bottom) = ("+self.left+", "+self.right+", "+self.top+", "+self.bot+"),\n")

    def get_roi(self) -> Tuple[Optional[int], Optional[int], Optional[int], Optional[int]]:
		print ("ROI set to: (left, right, top, bottom) = ("+self.left+", "+self.right+", "+self.top+", "+self.bot+"),\n")
		return self.left, self.right, self.top, self.bot

	def process_roi(self, num_data:int, V:int):
		self.set_roi_by_corner()
		circle_filter = dhm_utils.filter_fixed_point(self.hologram[self.left: self.right, self.top: self.bot], 3)
    	Back_filtered = dhm_utils.fourier_process(self.background[self.left: self.right, self.top: self.bot], circle_filter)
    	Back_filtered = np.exp(self._COMPLEX_J * np.angle(np.conj(Back_filtered)))

    	for data in range(num_data):
	        hologram_file_name = str(data + 1)
	        print('processing >>>>> ' + str(hologram_file_name))
	        #read from file system
	        hologram = self.hologram[self.left: self.right, self.top: self.bot]

	        # hologram, background = image_read_local()
	        # hologram, background = roi_apply(img1=hologram, img2=background, top=TOP, bot=BOT, left=LEFT, right=RIGHT)


	        holo_filtered = dhm_util.fourier_process(hologram, circle_filter)
	        holo_cleared = Back_filtered * holo_filtered
	        holo_apd = dhm_utils.apodization_process(holo_cleared)

	        phase_reconstructed, diffraction_distance, reconstructed, intensity_final = reconstruction_angular(holo_apd, V)
	        unwrapped_phase = dhm_utils.unwrap_phase(0 - phase_reconstructed)
	        height = dhm_utils.ackground_unit(unwrapped_phase * 3 / self.vector)
        	self._SHAR = np.squeeze(self._SHAR)






