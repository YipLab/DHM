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
h1.set_save_path("./result/")
h1.set_background_img("reference_background")
h1.add_hologram_img("tdhm_hologram")

# h1.set_roi_by_param(822, 2412, 1609, 3727)
h1.set_roi_by_param(0, 3000, 0, 4000)
h1.process_roi(filter_quadrant = 3, num_data = 1, k_factor = 1.5, volume_num= 2)

'''
 def process_roi(self, filter_quadrant: int = 3, num_data: int = 1, k_factor=1.5, vertical_step: int = 2):
     if self.get_roi() is False:
         self.set_roi_by_corner()

     circle_filter = dhm.interactive.filter_fixed_point(self.HOLOGRAM[0][self.left: self.right, self.top: self.bot],
                                                        filter_quadrant)
     back_filtered = dhm.utils.fourier_process(self.BACKGROUND[self.left: self.right, self.top: self.bot],
                                               circle_filter)
     back_filtered = np.exp(complex(0, 1) * np.angle(np.conj(back_filtered)))

     for data in range(num_data):
         hologram_file_name = str(data + 1)
         print('processing >>>>> ' + str(hologram_file_name))
         # read from file system
         hologram = self.HOLOGRAM[data][self.left: self.right, self.top: self.bot]

         holo_filtered = dhm.utils.fourier_process(hologram, circle_filter)
         holo_cleared = back_filtered * holo_filtered
         holo_apd = dhm.utils.apodization_process(holo_cleared, k_factor, self.expansion_main)

         phase_reconstructed, diffraction_distance, reconstructed, intensity_final = dhm.utils.reconstruction_angular(
             self, holo_apd, vertical_step)

         print('Focus plane of image	is >>>>>' + str(diffraction_distance) + 'um')
         tf.imwrite(str('./result/' + 'result_Angular_Hann_Intensity_' + str(data) + '.tiff'), reconstructed)
         tf.imwrite(str('./result/' + 'result_Angular_Hann_Intensity_22' + str(data) + '.tiff'), intensity_final)

         unwrapped_phase = dhm.utils.unwrap_phase(0 - phase_reconstructed)
         height = dhm.utils.background_unit(unwrapped_phase * 3 / self.vector)

         tf.imwrite(str('./result/' + 'result_Height_angle_' + '.tiff'), height)
         tf.imwrite(str('./result/' + 'result_Height_phase_angle' + '.tiff'), phase_reconstructed)

         self.SHAR = np.squeeze(self.SHAR)
         tf.imwrite(str('./result/' + 'result_Angular_Hann_shar_' + str(data) + '.tiff'), self.SHAR)

         self.HOLOGRAM[data] = np.ndarray(shape=(100, 100), dtype=np.uint8)  # release memory'''