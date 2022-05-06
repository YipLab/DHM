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
#import pandas as pd
from skimage.filters import gaussian
from skimage.restoration import unwrap_phase  # intall 'Microsoft's vcredist_x64.exe' if it not work 
# ( https://docs.microsoft.com/en-us/cpp/windows/latest-supported-vc-redist?view=msvc-170) 
#import openpyxl

import dhm.interactive
import dhm.utils

from typing import Optional, Tuple, List, Any

class HoloGram:

	_COMPLEX_J = complex(0, 1)
	SHAR = []
	
	def __init__(self, hologram, background):
		self.hologram = hologram
		self.background = background
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

		# Reconstruction parameter
		# self.rec_scale = 10
		# self.rec_pos = rec_scale / (-2)

		self.vector = 2 * self._diffraction_index * np.pi / self._wavelength
		self.delta = self._pixel_x / self._magnification

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

	def set_sys_param(self, pixel_x:float = 1.85, pixel_y:float = 1.85, diffraction_index:float = 1.52, \
						magnification:int = 10, wavelength:float = 0.640):
		self._pixel_x = pixel_x
		self._pixel_y = pixel_y  # micro-meter (unit)
		self._diffraction_index = diffraction_index
		self._magnification = magnification
		self._wavelength = wavelength  # 640nm

		self.vector = 2 * self._diffraction_index * np.pi / self._wavelength
		self.delta = self._pixel_x / self._magnification

	def get_sys_param(self) -> Tuple[Optional[float], Optional[float], Optional[float], Optional[int], Optional[float]]:
		print  ("pixel_x = "+str(self._pixel_x)+"um\n"\
				"pixel_y = "+str(self._pixel_y)+"um\n"\
				"diffraction_index = "+str(self._diffraction_index)+"\n"\
				"magnification = "+str(self._magnification)+"\n"\
				"wavelength = "+str(self._wavelength)+"nm\n"\
				)
		return self._pixel_x, self._pixel_y, self._diffraction_index, self._magnification, self._wavelength

	def set_expansion(self, expansion = 100): 
		self._expansion = expansion
	
	def get_expansion(self, expansion = 100) -> int:
		print ("expansion factor = "+str(self._expansion)+"\n")
		return self._expansion

	def holo_roi_show(self):
		print ("Currently viewing ROI: (left, right, top, bottom) = ("+str(self.left)+", "+str(self.right)+", "+str(self.top)+", "+str(self.bot)+"),\n"\
			"Whole image size is: ("+str(self._shape_x)+", "+str(self._shape_y)+")")
		plt.imshow(self.hologram[self.left: self.right, self.top: self.bot], cmap='gray')  # 8-bit grey scale
		plt.ginput(1)

	def holo_show(self):
		print ("Currently viewing the whole image, image size is: ("+str(self._shape_x)+", "+str(self._shape_y)+")")
		plt.imshow(self.hologram, cmap='gray')  # 8-bit grey scale
		plt.ginput(1)

	def set_roi_by_centre(self, radius = 200):
		print ("Currently viewing the whole image, image size is: ("+str(self._shape_x)+", "+str(self._shape_y)+")")
		print ("Set ROI by Centre: Click to set the centre of ROI with a raidus of :"+str(radius))
		plt.imshow(self.hologram, cmap='gray')  # 8-bit grey scale
		roi_x = plt.ginput(1)
		self.top = np.int(np.subtract(roi_x[0][0], radius))
		self.bot = np.int(np.add(roi_x[0][0], radius))
		self.left = np.int(np.subtract(roi_x[0][1], radius))
		self.right = np.int(np.add(roi_x[0][1], radius))
		print ("ROI updated to: (left, right, top, bottom)= ("+str(self.left)+", "+str(self.right)+", "+str(self.top)+", "+str(self.bot)+"),\n")

	def set_roi_by_corner(self):
		print ("Currently viewing the whole image, image size is: ("+str(self._shape_x)+", "+str(self._shape_y)+")")
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
		print ("ROI updated to: (left, right, top, bottom)= ("+str(self.left)+", "+str(self.right)+", "+str(self.top)+", "+str(self.bot)+"),\n")


	def set_roi_by_param(self, left: int, right: int, top: int, bottom: int) -> int:
		self.top = top
		self.bot = bottom
		self.left = left
		self.right = right
		print ("ROI set to: (left, right, top, bottom) = ("+str(self.left)+", "+str(self.right)+", "+str(self.top)+", "+str(self.bot)+"),\n")

	def get_roi(self) -> Optional[Tuple[int, int, int, int]]:
		print ("ROI set to: (left, right, top, bottom) = ("+str(self.left)+", "+str(self.right)+", "+str(self.top)+", "+str(self.bot)+"),\n")
		return self.left, self.right, self.top, self.bot

	def process_roi(self, filter_quadrant:int = 3, num_data:int = 1, k_factor = 1.5, vertical_step:int = 2, rec_scale:int = 10):
		# if (self.get_roi() == [None, None, None, None]):
		# 	print("ROI not set yet. Please set ROI")
		# 	self.set_roi_by_corner()
		self.set_roi_by_corner()
		
		circle_filter = dhm.interactive.filter_fixed_point(self.hologram[self.left: self.right, self.top: self.bot], filter_quadrant)
		back_filtered = dhm.utils.fourier_process(self.background[self.left: self.right, self.top: self.bot], circle_filter)
		back_filtered = np.exp(self._COMPLEX_J * np.angle(np.conj(back_filtered)))

		for data in range(num_data):
			hologram_file_name = str(data + 1)
			print('processing >>>>> ' + str(hologram_file_name))
			#read from file system
			hologram = self.hologram[self.left: self.right, self.top: self.bot]

			holo_filtered = dhm.utils.fourier_process(hologram, circle_filter)
			holo_cleared = back_filtered * holo_filtered
			holo_apd = dhm.utils.apodization_process(holo_cleared, k_factor, self._expansion)

			phase_reconstructed, diffraction_distance, reconstructed, intensity_final = dhm.utils.reconstruction_angular(self, holo_apd, vertical_step, self.vector, self.delta, self._expansion, rec_scale)
			
			print('Focus plane of image    is >>>>>' + str(diffraction_distance) + 'um')
			tf.imwrite(str('./result/' + 'result_Angular_Hann_Intensity_' + str(data) + '.tiff'), reconstructed)
			tf.imwrite(str('./result/' + 'result_Angular_Hann_Intensity_22' + str(data) + '.tiff'), intensity_final)

			unwrapped_phase = dhm.utils.unwrap_phase(0 - phase_reconstructed)
			height = dhm.utils.background_unit(unwrapped_phase * 3 / self.vector)

			tf.imwrite(str('./result/' + 'result_Height_angle_' + '.tiff'), height)
			tf.imwrite(str('./result/' + 'result_Height_phase_angle' + '.tiff'), phase_reconstructed)

			self.SHAR = np.squeeze(self.SHAR)
			tf.imwrite(str('./result/' + 'result_Angular_Hann_shar_' + str(data) + '.tiff'), self.SHAR)






