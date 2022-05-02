#!/usr/bin/env python3

import os.path
import sys

import dhm.core
import dhm.interactive
import dhm.utils
# import dhm.gui


holo, bgd = dhm.interactive.read_local("../../Example Images/", "reference_background", "tdhm_hologram")
h1 = dhm.core.HoloGram(holo, bgd)
# h1.set_roi_by_param(100, 300, 200,400)
h1.process_roi(filter_quadrant = 3, num_data = 1, k_factor = 1.5, vertical_step = 2, rec_scale = 10)