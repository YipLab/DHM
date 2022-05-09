# #####################################################################################################################
# This program is for digital holographic microscope
# Main Idea:
#			Auto-Focusing with Angular Spectrum (Fourier sharpness);
#			Auto-Fourier Filtering;
#			Phase unwrapping
#
# Camera Info: FLIR BFS-U3-120S4M-CS, Pixel size: 1.85um, (4000 x 3000)
#
# Date: 2022-Jan-12
# #####################################################################################################################

##DHM_core

import numpy as np
import tifffile as tf
from tqdm import tqdm
import matplotlib.pyplot as plt
import math
from skimage.restoration import unwrap_phase
# On Windows, intall 'Microsoft's vcredist_x64.exe' if it does not work 
# ( https://docs.microsoft.com/en-us/cpp/windows/latest-supported-vc-redist?view=msvc-170) 

import dhm.interactive
import dhm.utils

from typing import Optional, Tuple, List, Any


class HoloGram:
    SHAR = []
    HOLOGRAM = []
    BACKGROUND = np.ndarray(shape=(300, 400), dtype=np.uint16)

    # System Parameter (Do not put these parameter into "self", or they won't be changed after)
    _pixel_x = 1.85
    _pixel_y = 1.85  # micro-meter (unit)
    _refractive_index = 1.52
    _magnification = 10
    _wavelength = 0.640  # 640nm
    _expansion = 100

    _shape_x = 0
    _shape_y = 0

    _METHOD = {
        "FA": "Fourier Analysis",
        "ST": "Statistic Analysis",
        "GB": "Gaussian Blur",
        "PO": "Polynomial method",
        "HA": "Hanning Filter",
        "FW": "Flat Window Filter",
    }

    def __init__(self):

        # Reconstruction parameter
        self.recon_enable = False
        self.rec_scale = 10
        self.rec_pos = self.rec_scale / (-2)

        # self._rec_start = 0
        # self._rec_end = 0
        # self._rec_step = 0
        # self.detect_method = ''

        # self.vector = 2 * self._refractive_index * np.pi / self._wavelength
        # self.delta = self._pixel_x / self._magnification

        # ROI Settings
        self.left = None
        self.right = None
        self.top = None
        self.bot = None

        # Filter Settings
        # Hanning Filter and Flat Window filter
        filter_type = ''
        size_rate = 1.2

        # Noise and Background
        # Gaussian Blur and Polynomial method
        leveling_method = ''
        filter_size = 80

        # Save Settings
        # save_height_map = False
        # save_phase_map = False
        # save_wrapped_phase = False
        # save_refocused_volume = False

        # Directory settings
        self.read_path = ''
        self.save_path = ''

    def set_background_img(self, bgd_file_name):
        self.BACKGROUND = np.array(tf.imread(str(self.read_path + '/' + bgd_file_name + '.tiff'))[:, :], dtype=float)
        self._shape_x = self.BACKGROUND.shape[0]
        self._shape_y = self.BACKGROUND.shape[1]
        print(f"Background is set, resolution is ({self._shape_x},{self._shape_y})")

    def add_hologram_img(self, holo_file_name):

        hologram = np.array(plt.imread(str(self.read_path + holo_file_name + '.tiff'))[:, :], dtype=float)

        if (hologram.shape != self.BACKGROUND.shape):
            print(f"Background resolution is ({self._shape_x},{self._shape_y}), ",
                  f"Hologram resolution is ({hologram.shape[0]},{hologram.shape[1]}),",
                  "\n- Hologram and Background resolutions do not match!")
            raise Exception("NON MATCHING RESOLUTIONS")
        self.HOLOGRAM.append(hologram)

    def set_read_path(self, read_path):
        self.read_path = read_path

    def set_save_path(self, save_path):
        self.save_path = save_path

    def set_sys_param(self, pixel_x: float = 1.85, pixel_y: float = 1.85, refractive_index: float = 1.52,
                      magnification: int = 10, wavelength: float = 0.640):
        self._pixel_x = pixel_x
        self._pixel_y = pixel_y  # micro-meter (unit)
        self._refractive_index = refractive_index
        self._magnification = magnification
        self._wavelength = wavelength  # 640nm

        self.vector = 2 * refractive_index * np.pi / wavelength
        self.delta = pixel_x / magnification

    def set_expansion(self, expansion: int = 100):
        self._expansion = expansion

    def set_recon_param(self, recon_enable: bool, rec_start: float = 0.00, rec_end: float = 0.00,
                        rec_step: float = 0.00, detect_method: str = "FA"):
        if recon_enable is True:
            self.recon_enable = recon_enable
            self._rec_start = rec_start
            self._rec_end = rec_end
            self._rec_step = rec_step
            self.detect_method = detect_method

    def get_sys_param(self) -> Tuple[Optional[float], Optional[float], Optional[float], Optional[int], Optional[float]]:
        print("## System Paramters ##",
              f"\npixel_x = {self._pixel_x}um, \npixel_y = {self._pixel_y}um, \nrefractive_index = {self._refractive_index},"
              f"\nmagnification = {self._magnification}, \nwavelength =  {self._wavelength}nm\n")
        return self._pixel_x, self._pixel_y, self._refractive_index, self._magnification, self._wavelength

    def get_expansion(self, expansion=100) -> int:
        print(f"expansion factor = {self._expansion}")
        return self._expansion

    def get_recon_param(self) -> Tuple[Optional[float], Optional[float], Optional[float], Optional[str]]:
        if (self.recon_enable is False):
            print("Reconstruction is disabled.")
        else:
            print("## Reconstruction Paramters ##",
                  f"\nrec_start = {self._rec_start}um, \nrec_end = {self._rec_end}um, \nrec_step = {self._rec_step}um,",
                  f"\ndetect_method is {self._METHOD[self.detect_method]}\n")
            return self._rec_start, self._rec_end, self._rec_step, self.detect_method

    def holo_roi_show(self):
        print(
            f"Currently viewing ROI: (left, right, top, bottom) = ({self.left}, {self.right}, {self.top}, {self.bot})",
            f"\nWhole image size is: ({self._shape_x}), {self._shape_y})")
        plt.imshow(self.HOLOGRAM[0][self.left: self.right, self.top: self.bot], cmap='gray')  # 8-bit grey scale
        plt.ginput(1)

    def holo_show(self):
        print(f"Currently viewing the whole image, image size is: ({self._shape_x}), {self._shape_y})")
        plt.imshow(self.HOLOGRAM[0], cmap='gray')  # 8-bit grey scale
        plt.ginput(1)

    def set_roi_by_centre(self, radius=200):
        print(f"Currently viewing the whole image, image size is: ({self._shape_x}), {self._shape_y})")
        print(f"Set ROI by Centre: Click to set the centre of ROI with a raidus of {radius} pixels")
        plt.imshow(self.HOLOGRAM[0], cmap='gray')  # 8-bit grey scale
        roi_x = plt.ginput(1)
        self.top = np.int(np.subtract(roi_x[0][0], radius))
        self.bot = np.int(np.add(roi_x[0][0], radius))
        self.left = np.int(np.subtract(roi_x[0][1], radius))
        self.right = np.int(np.add(roi_x[0][1], radius))
        print(f"ROI updated to: (left, right, top, bottom)= ({self.left}, {self.right}, {self.top}, {self.bot})")

    def set_roi_by_corner(self):
        print(f"Currently viewing the whole image, image size is: ({self._shape_x}), {self._shape_y})")
        print("Set ROI by Corner: Click the desired top left and bottom right corner to set ROI coordinates")
        plt.imshow(self.HOLOGRAM[0], cmap='gray')  # 8-bit grey scale
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
        print(f"ROI updated to: (left, right, top, bottom)= ({self.left}, {self.right}, {self.top}, {self.bot})")

    def set_roi_by_param(self, left: int, right: int, top: int, bottom: int) -> int:
        self.top = top
        self.bot = bottom
        self.left = left
        self.right = right
        print(f"ROI set to: (left, right, top, bottom)= ({self.left}, {self.right}, {self.top}, {self.bot})")

    def get_roi(self) -> Optional[Tuple[int, int, int, int]]:
        if (self.left, self.right, self.top, self.bot) == (None, None, None, None):
            print("ROI not set yet. Please set ROI")
            return False
        else:
            print(f"ROI set to: (left, right, top, bottom)= ({self.left}, {self.right}, {self.top}, {self.bot})")
        return self.left, self.right, self.top, self.bot

    def process_roi(self, filter_quadrant: int = 3, num_data: int = 1, k_factor=1.5, vertical_step: int = 2):
        if (self.get_roi() is False):
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
            holo_apd = dhm.utils.apodization_process(holo_cleared, k_factor, self._expansion)

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

            self.HOLOGRAM[data] = np.ndarray(shape=(100, 100), dtype=np.uint8)  # release memory
