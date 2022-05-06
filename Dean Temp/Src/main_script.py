#!/usr/bin/env python3

import os.path
import sys

import numpy as np
import dhm.core
import dhm.interactive
import dhm.utils
# import dhm.gui


# holo, bgd = dhm.interactive.read_local("../../Example Images/", "reference_background", "tdhm_hologram")

h1 = dhm.core.HoloGram()
h1.set_sys_param(pixel_x = 1.85, pixel_y = 1.85, refractive_index = 1.52, \
						magnification = 10, wavelength = 0.640)
h1.get_sys_param()
h1.set_recon_param(recon_enable=True, rec_start=0.00, rec_end=0.00, rec_step=0.00, detect_method = "FA")
h1.get_recon_param()

h1.set_read_path("../../Example Images/")
h1.set_background_img("reference_background")
h1.add_hologram_img("tdhm_hologram")

# h1.set_roi_by_param(100, 300, 200,400)
# h1.process_roi(filter_quadrant = 3, num_data = 1, k_factor = 1.5, vertical_step = 2, rec_scale = 10)