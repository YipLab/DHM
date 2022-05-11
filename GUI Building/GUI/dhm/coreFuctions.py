# #####################################################################################################################
# This program is for digital holographic microscope
# Main Idea:
#           Auto-Focusing with Angular Spectrum (Fourier sharpness);
#           Auto-Fourier Filtering;
#           Phase unwrapping
#
# Camera Info: BFS-U3-120S4M-CS, Pixel size: 1.85um, (4000 x 3000)
#
# Date: 2022-Jan-12
# #####################################################################################################################

# DHM_core

import numpy as np
import os
import matplotlib.pyplot as plt
from skimage.restoration import unwrap_phase
# On Windows, install 'Microsoft's vcredist_x64.exe' if it does not work
# ( https://docs.microsoft.com/en-us/cpp/windows/latest-supported-vc-redist?view=msvc-170)

from dhm import interactive
from dhm import utils
from typing import Optional, Tuple, Any


class HoloGram:
    SHAR = []
    HOLOGRAM = np.ndarray(shape=(3000, 4000), dtype=np.uint16)
    BACKGROUND = np.ndarray(shape=(3000, 4000), dtype=np.uint16)

    # Dependant Parameter
    Processed_Background = np.ndarray(shape=(3000, 4000), dtype=np.uint16)
    Order_Filter = np.ndarray(shape=(3000, 4000), dtype=np.uint16)

    # System Parameters
    pixel_x_main = 1.85
    pixel_y_main = 1.85  # micro-meter (unit)
    refractive_index_main = 1.52
    magnification_main = 20
    wavelength_main = 0.640  # 640nm

    # Reconstruction Parameters
    recon_enable_main = False
    rec_start_main = 0.0
    rec_end_main = 0.0
    rec_step_main = 0.0
    detect_method_main = "Fourier Analysis"

    # Filter Parameters
    filter_type_main = "Hann"
    filter_rate_main = 1.2
    filter_quadrant_main = "1"
    expansion_main = 100

    # What to Save
    height_map_main = True
    phase_map_main = False
    wrapped_phase_main = False
    refocused_volume_main = False

    # Variable to Save
    Height_Map = None
    Phase_Map = None
    Wrapped_phase = None
    Refocused_Volume = None

    # Processing Parameters
    leveling_method_main = "Gaussian Blur"
    gaussian_size_main = 80
    holo_total_main = 1
    holo_start_main = 0

    # ROI Setting
    ROI_enable = False

    # Directory Settings
    read_path_main = ''
    save_path_main = ''

    shape_x_main = 0
    shape_y_main = 0

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
        self.recon_enable_main = False
        self.rec_scale = 10
        self.rec_pos = self.rec_scale / (-2)
        self.height_factor = 2 * self.refractive_index_main * np.pi / self.wavelength_main
        # self.vector = 2 * self.refractive_index_main * np.pi / self.wavelength_main
        self.delta = self.pixel_x_main / self.magnification_main

        # ROI Settings
        self.left = None
        self.right = None
        self.top = None
        self.bot = None

    def set_background_img(self, read_path_back: str = '', bgd_file_name: str = 'ref.tiff'):
        if os.path.isfile(str(read_path_back + bgd_file_name)):
            self.BACKGROUND = np.array(plt.imread(str(read_path_back + bgd_file_name))[:, :], dtype=float)
            self.shape_x_main = self.BACKGROUND.shape[0]
            self.shape_y_main = self.BACKGROUND.shape[1]
            print(f"Background is set, resolution is ({self.shape_x_main},{self.shape_y_main})")
        else:
            # How to show this in the GUI ???? ###############################################
            print(str(read_path_back + bgd_file_name + '.tiff'))
            print("Please type in a correct address!")

    def add_hologram_img(self, holo_file_name):
        if os.path.isfile(str(self.read_path_main + holo_file_name + '.tiff')):
            self.HOLOGRAM = np.array(plt.imread(str(self.read_path_main + holo_file_name + '.tiff'))[:, :], dtype=float)

            if self.HOLOGRAM.shape != self.BACKGROUND.shape:
                print(f"Background resolution is ({self.shape_x_main},{self.shape_y_main}), ",
                      f"Hologram resolution is ({self.HOLOGRAM.shape[0]},{self.HOLOGRAM.shape[1]}),",
                      "\n- Hologram and Background resolutions do not match!")
                raise Exception("NON MATCHING RESOLUTIONS")
        else:
            # How to show this in the GUI ???? ###############################################
            print(str(self.read_path_main + holo_file_name + '.tiff'))
            print("Please type in a correct address for hologram!")

    def set_read_path(self, read_path: str):
        self.read_path_main = read_path

    def set_save_path(self, save_path: str):
        self.save_path_main = save_path

    def set_sys_param(self, pixel_x: float = 1.85, pixel_y: float = 1.85, refractive_index: float = 1.52,
                      magnification: int = 20, wavelength: float = 0.640):
        self.pixel_x_main = pixel_x
        self.pixel_y_main = pixel_y  # micro-meter (unit)
        self.refractive_index_main = refractive_index
        self.magnification_main = magnification
        self.wavelength_main = wavelength / 1000  # unit micrometer

        self.height_factor = 2 * refractive_index * np.pi / wavelength
        self.delta = pixel_x / magnification

    def set_roi_para(self, roi_enable: bool):
        self.ROI_enable = roi_enable

    def set_filter_para(self, expansion: int = 100, filter_type: str = "Hann", filter_rate: float = 1.2,
                        filter_quadrant: str = '1'):
        self.expansion_main = expansion
        self.filter_type_main = filter_type
        self.filter_rate_main = filter_rate
        self.filter_quadrant_main = filter_quadrant

    def set_recon_param(self, recon_enable: bool, rec_start: float = 0.00, rec_end: float = 0.00,
                        rec_step: float = 0.00, detect_method: str = "FA"):
        self.recon_enable_main = recon_enable
        self.rec_start_main = rec_start
        self.rec_end_main = rec_end
        self.rec_step_main = rec_step
        self.detect_method_main = detect_method

    def set_processing_para(self, leveling_method: str, gaussian_size: int, holo_count: int, holo_start: int):
        self.leveling_method_main = leveling_method
        self.gaussian_size_main = gaussian_size
        self.holo_total_main = holo_count
        self.holo_start_main = holo_start

    def set_what_to_save(self, height_map: bool, phase_map: bool, wrapped_phase: bool, refocused_volume: bool):
        self.height_map_main = height_map
        self.phase_map_main = phase_map
        self.wrapped_phase_main = wrapped_phase
        self.refocused_volume_main = refocused_volume

    def get_sys_param(self) -> Tuple[Optional[float], Optional[float], Optional[float], Optional[int], Optional[float]]:
        print("## System Parameters ##",
              f"\npixel_x = {self.pixel_x_main}um, \npixel_y = {self.pixel_y_main}um, "
              f"\nrefractive_index = {self.refractive_index_main}, "
              f"\nmagnification = {self.magnification_main}, \nwavelength =  {self.wavelength_main}nm\n")
        return self.pixel_x_main, self.pixel_y_main, self.refractive_index_main, self.magnification_main, self.wavelength_main

    def get_expansion(self) -> int:
        print(f"expansion factor = {self.expansion_main}")
        return self.expansion_main

    def get_recon_param(self) -> Tuple[Optional[float], Optional[float], Optional[float], Optional[str]]:
        if self.recon_enable_main is False:
            print("Reconstruction is disabled.")
        else:
            print("## Reconstruction Parameters ##",
                  f"\nrec_start = {self.rec_start_main}um, "
                  f"\nrec_end = {self.rec_end_main}um, \nrec_step = {self.rec_step_main}um,",
                  f"\ndetect_method is {self._METHOD[self.detect_method_main]}\n")
            return self.rec_start_main, self.rec_end_main, self.rec_step_main, self.detect_method_main

    def holo_roi_show(self):
        print(
            f"Currently viewing ROI: (left, right, top, bottom) = ({self.left}, {self.right}, {self.top}, {self.bot})",
            f"\nWhole image size is: ({self.shape_x_main}), {self.shape_y_main})")
        plt.imshow(self.HOLOGRAM[0][self.left: self.right, self.top: self.bot], cmap='gray')  # 8-bit grey scale
        plt.ginput(1)

    def holo_show(self):
        print(f"Currently viewing the whole image, image size is: ({self.shape_x_main}), {self.shape_y_main})")
        plt.imshow(self.HOLOGRAM[0], cmap='gray')  # 8-bit grey scale
        plt.ginput(1)

    def set_roi_by_centre(self, radius=200):
        print(f"Currently viewing the whole image, image size is: ({self.shape_x_main}), {self.shape_y_main})")
        print(f"Set ROI by Centre: Click to set the centre of ROI with a radius of {radius} pixels")
        plt.imshow(self.HOLOGRAM[0], cmap='gray')  # 8-bit grey scale
        roi_x = plt.ginput(1)
        self.top = np.int(np.subtract(roi_x[0][0], radius))
        self.bot = np.int(np.add(roi_x[0][0], radius))
        self.left = np.int(np.subtract(roi_x[0][1], radius))
        self.right = np.int(np.add(roi_x[0][1], radius))
        print(f"ROI updated to: (left, right, top, bottom)= ({self.left}, {self.right}, {self.top}, {self.bot})")

    def set_roi_by_corner(self):
        print(f"Currently viewing the whole image, image size is: ({self.shape_x_main}), {self.shape_y_main})")
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

    def set_roi_by_param(self, left: int, right: int, top: int, bottom: int):
        self.top = top
        self.bot = bottom
        self.left = left
        self.right = right
        print(f"ROI set to: (left, right, top, bottom)= ({self.left}, {self.right}, {self.top}, {self.bot})")

    def get_roi(self) -> bool | tuple[Any, Any, Any, Any]:
        if (self.left, self.right, self.top, self.bot) == (None, None, None, None):
            print("ROI not set yet. Please set ROI")
            return False
        else:
            print(f"ROI set to: (left, right, top, bottom)= ({self.left}, {self.right}, {self.top}, {self.bot})")
        return self.left, self.right, self.top, self.bot

    def filter_background_process(self):
        if not self.ROI_enable:
            self.Order_Filter = interactive.filter_fixed_point(hologram_raw=self.HOLOGRAM,
                                                               quadrant=self.filter_quadrant_main,
                                                               filter_rate=self.filter_rate_main,
                                                               filter_type=self.filter_type_main)

            background_filtered = utils.fourier_process(self.BACKGROUND, self.Order_Filter)
            self.Processed_Background = np.exp(complex(0, 1) * np.angle(np.conj(background_filtered)))
        else:
            print("Will do")

    def hologram_process(self):
        reconstructed_map = None
        hologram = utils.fourier_process(self.HOLOGRAM, self.Order_Filter) * self.Processed_Background
        if self.recon_enable_main:
            print("will do")
        else:
            reconstructed_map = hologram

        self.Wrapped_phase = np.angle(reconstructed_map)
        self.Phase_Map = unwrap_phase(self.Wrapped_phase)
        self.Height_Map = self.Phase_Map / self.height_factor
