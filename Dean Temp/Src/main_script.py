#!/usr/bin/env python3

import os.path
import sys

import numpy as np
import dhm.core
import dhm.interactive
import dhm.utils
# import dhm.gui


# holo, bgd = dhm.interactive.read_local("../../Example Images/", "reference_background", "tdhm_hologram")
nda = np.ndarray(shape=(3000,4000), dtype=np.uint8)
h1 = dhm.core.HoloGram(nda, nda)
h1.set_sys_param(pixel_x = 1.85, pixel_y = 1.85, diffraction_index = 1.52, \
						magnification = 10, wavelength = 0.640)
h1.get_sys_param()
# h1.set_roi_by_param(100, 300, 200,400)
# h1.process_roi(filter_quadrant = 3, num_data = 1, k_factor = 1.5, vertical_step = 2, rec_scale = 10)