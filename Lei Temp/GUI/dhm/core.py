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
import tifffile as tf
import matplotlib.pyplot as plt
from skimage.restoration import unwrap_phase
# On Windows, install 'Microsoft's vcredist_x64.exe' if it does not work
# ( https://docs.microsoft.com/en-us/cpp/windows/latest-supported-vc-redist?view=msvc-170)

# import utils
# import interactive
from typing import Optional, Tuple, Any

# ======================= Cores =========================#
from tqdm import tqdm
import pandas as pd
from skimage.filters import gaussian

# ======================= interactive =====================#
import math


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
    HEIGHT_MAP = None
    PHASE_MAP = None
    WRAPPED_PHASE = None
    REFOCUSED_VOLUME = None

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

    def set_background_img(self, read_path_back: str = '', bgd_file_name: str = 'ref'):
        if os.path.isfile(read_path_back + bgd_file_name):
            self.BACKGROUND = np.array(plt.imread(read_path_back + bgd_file_name)[:, :], dtype=float)
            self.shape_x_main = self.BACKGROUND.shape[0]
            self.shape_y_main = self.BACKGROUND.shape[1]
            print(f"Background is set, resolution is ({self.shape_x_main},{self.shape_y_main})")
        else:
            # How to show this in the GUI ???? ###############################################
            print(str(read_path_back + bgd_file_name + '.tiff'))
            print("Please type in a correct address!")

    def add_hologram_img(self, holo_file_name):
        if os.path.isfile(self.read_path_main + holo_file_name + '.tiff'):
            self.HOLOGRAM = np.array(plt.imread(self.read_path_main + holo_file_name + '.tiff')[:, :], dtype=float)
            self.shape_x_main = self.HOLOGRAM.shape[0]
            self.shape_y_main = self.HOLOGRAM.shape[1]
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

    def get_roi(self) -> Tuple[Any, Any, Any, Any]:
        if (self.left, self.right, self.top, self.bot) == (None, None, None, None):
            print("ROI not set yet. Please set ROI")
            return False
        else:
            print(f"ROI set to: (left, right, top, bottom)= ({self.left}, {self.right}, {self.top}, {self.bot})")
        return self.left, self.right, self.top, self.bot

    def save_results(self, num):
        if self.save_path_main == '':
            print("Set your save_path first")
            return
        if self.height_map_main is True:
            tf.imwrite(f"{self.save_path_main}result_HEIGHT_MAP_{str(num)}.tiff", self.HEIGHT_MAP)
            print(f"Saving height map at {self.save_path_main}...")
        if self.phase_map_main is True:
            tf.imwrite(f"{self.save_path_main}result_PHASE_MAP_{str(num)}.tiff", self.PHASE_MAP)
            print(f"Saving phase map at {self.save_path_main}...")
        if self.wrapped_phase_main is True:
            tf.imwrite(f"{self.save_path_main}result_WRAPPED_PHASE_{str(num)}.tiff", self.WRAPPED_PHASE)
            print(f"Saving wrapped phase at {self.save_path_main}...")
        if self.refocused_volume_main is True:
            tf.imwrite(f"{self.save_path_main}result_REFOCUSED_VOLUME_{str(num)}.tiff", self.REFOCUSED_VOLUME)
            print(f"Saving refocused volume at {self.save_path_main}...")

    def filter_background_process(self):
        if not self.ROI_enable:
            print("filter processing")
            self.Order_Filter = self.filter_fixed_point(hologram_raw=self.HOLOGRAM,
                                                        quadrant=self.filter_quadrant_main,
                                                        filter_rate=self.filter_rate_main,
                                                        filter_type=self.filter_type_main)
            print('background processing')
            background_filtered = self.fourier_process(self.BACKGROUND, self.Order_Filter)
            self.Processed_Background = np.exp(complex(0, 1) * np.angle(np.conj(background_filtered)))

        else:
            print("Will do the ROI")

    def hologram_process(self):
        print("hologram Fourier processing")
        reconstructed_map = None
        hologram = self.fourier_process(self.HOLOGRAM, self.Order_Filter)
        print("hologram clean processing")
        hologram = hologram * self.Processed_Background
        print("hologram processed")
        if self.recon_enable_main:
            print("will do the reconstruction")
        else:
            reconstructed_map = hologram

        self.WRAPPED_PHASE = np.angle(reconstructed_map)
        self.PHASE_MAP = unwrap_phase(self.WRAPPED_PHASE)
        self.HEIGHT_MAP = self.PHASE_MAP / self.height_factor
        self.HEIGHT_MAP = self.background_unit(self.HEIGHT_MAP)


    # ================================= interactive =================================================#
    # ================================= interactive =================================================#
    # ================================= interactive =================================================#
    def filter_fixed_point(self, hologram_raw, quadrant: str = '1', filter_rate: float = 1.2,
                           filter_type: str = 'Hann'):
        frequency = np.fft.fftshift(np.fft.fft2(hologram_raw))
        shape_vertical, shape_horizontal = np.shape(frequency)
        center_x = None
        center_y = None

        # If First Quadrant
        if quadrant == '1':
            first_quadrant = frequency[1: int(math.floor(shape_vertical / 2) - 30),
                             int(math.floor(shape_horizontal / 2) + 30):shape_horizontal - 30]
            indices = np.where(first_quadrant == np.amax(first_quadrant))
            center_x = indices[0]
            center_y = indices[1] + int(math.floor(shape_horizontal / 2) + 30)

        # If Second Quadrant
        elif quadrant == '2':
            second_quadrant = frequency[1: int(math.floor(shape_vertical / 2) - 30),
                              1:int(math.floor(shape_horizontal / 2) - 30)]
            indices = np.where(second_quadrant == np.max(second_quadrant))
            center_x = indices[0]
            center_y = indices[1]

        # If Third Quadrant
        elif quadrant == '3':
            third_quadrant = frequency[int(math.floor(shape_vertical / 2) + 30):shape_vertical - 30,
                             1:int(math.floor(shape_horizontal / 2) - 30)]
            indices = np.where(third_quadrant == np.amax(third_quadrant))
            center_x = indices[0] + int(math.floor(shape_vertical / 2) + 30)
            center_y = indices[1]

        # If Fourth Quadrant
        elif quadrant == '4':
            fourth_quadrant = frequency[int(math.floor(shape_vertical / 2) + 30): shape_vertical - 30,
                              int(math.floor(shape_horizontal / 2) + 30):shape_horizontal - 30]
            indices = np.where(fourth_quadrant == np.amax(fourth_quadrant))
            center_x = indices[0] + int(math.floor(shape_vertical / 2) + 30)
            center_y = indices[1] + int(math.floor(shape_horizontal / 2) + 30)

        distance = np.sqrt(np.power(np.abs(center_x - int(shape_vertical / 2)), 2)
                           + np.power(np.abs(int(shape_horizontal / 2) - center_y), 2))
        radius = int((distance / 3) * filter_rate)

        mesh_m, mesh_n = np.meshgrid(np.arange(0, shape_horizontal), np.arange(0, shape_vertical))
        region = np.sqrt((mesh_n - float(center_x)) ** 2 + (mesh_m - float(center_y)) ** 2)
        circle_window = np.array(region <= radius)
        if filter_type == "Hann":
            filter_hann = self.hanning_filter(shape_vertical, shape_horizontal, center_x, center_y, radius)
            print('circel_window', np.shape(circle_window))
            print('filter_hann', np.shape(filter_hann))
            circle_window = circle_window * filter_hann
            print("hann finished")
        return circle_window

    # ======================= utils =================================================================#
    def hanning_filter(self, m_x, n_y, c_x, c_y, r):
        print(m_x, n_y, c_x, c_y, r)
        hann = np.sqrt(np.outer(np.hanning(r * 2), np.hanning(r * 2)))
        hann = np.pad(hann, ((int(c_x - r), int(m_x - c_x - r)), (int(c_y - r), int(n_y - c_y - r))), 'constant')
        print(np.shape(hann))
        return hann

    def fourier_process(self, img_pre, filter_pre):
        fourier_pre = np.fft.fft2(img_pre)
        fourier_selected = np.fft.ifftshift(np.fft.fftshift(fourier_pre) * filter_pre)
        fourier_selected = np.fft.ifft2(fourier_selected)

        return fourier_selected

    def flat_window(self, l_end, l_begin, a, b, k_fac):
        line = np.linspace(1, l_end, l_end)

        interval0 = [1 if (i < (int(l_end - l_begin) / 2)) else 0 for i in line]
        interval1 = [1 if ((((l_end - l_begin) / 2) <= i) and (i <= int(l_end + l_begin) / 2)) else 0 for i in line]
        interval2 = [1 if (i > ((l_end + l_begin) / 2)) else 0 for i in line]
        w1 = np.power(np.cos(a * ((2 * line) / int(l_end - l_begin) - 1)), k_fac) * interval0
        w1[np.isnan(w1)] = 0
        w2 = interval1
        w3 = np.power(np.cos(b * ((2 * line) / (l_end + l_begin + 2) - 1)), k_fac) * interval2
        w3[np.isnan(w3)] = 0

        w = w1 + w2 + w3
        return w

    def apodization_process(self, img, k_factor, expansion):
        l0x, l0y = img.shape
        l0x = l0x - (expansion * 3)
        l0y = l0y - (expansion * 3)

        holo = np.pad(img, pad_width=expansion, mode='edge')
        lx, ly = holo.shape

        ax = - (np.pi / 2) * (lx - l0x) / (l0x - lx + 2)
        bx = (np.pi / 2) * (lx + l0x + 2) / (lx - l0x - 2)
        ay = - (np.pi / 2) * (ly - l0y) / (l0y - ly + 2)
        by = (np.pi / 2) * (ly + l0y + 2) / (ly - l0y - 2)

        wx = self.flat_window(lx, l0x, ax, bx, k_factor)
        wy = self.flat_window(ly, l0y, ay, by, k_factor)

        x, y = np.meshgrid(wy, wx)

        window = x * y

        img_processed = holo * window

        return img_processed

    def sharpness_test(self, img_raw, shar):
        img = self.background_unit(img_raw)
        img_gaussian = gaussian(img, sigma=1)

        fourier = np.fft.fftshift(np.fft.fft2(np.abs(img_gaussian)))
        sharp = np.sum(np.log(1 + abs(fourier)))
        # n_img, m_img = img.shape

        # sharp = np.sum(np.square(np.absolute(img) - np.mean(img_gaussian))) / (n_img * m_img)
        # sharp = cv2.Laplacian(img_gaussian, cv2.CV_64F).var()
        shar.append(img)
        return sharp

    # in continuous mode, should not use Angular
    def angular_spectrum(self, hologram, img_res, kz, mask, term, recon_scale, recon_start, expansion, vol):
        image_phase = []
        intensity = []
        sharpness_res = []
        diffraction_dis = []
        gaussian_img = []

        bar_first = tqdm(range(1, vol))

        for z in bar_first:
            bar_first.set_description("Processing_Angular " + str(term) + ":" + str(int(z + 1)))
            df = recon_start + z * recon_scale / vol
            c = np.where(mask, img_res * np.exp(complex(0, 1) * kz * df), 0)
            e = np.fft.ifft2(np.fft.ifftshift(c))
            e = e[expansion: expansion + hologram.HOLOGRAM[0].shape[0],
                expansion: expansion + hologram.HOLOGRAM[0].shape[1]]

            reconstructed_in = np.real(e * np.conjugate(e))
            # sharp_value_intensity = cv2.Laplacian(reconstructed_in, cv2.CV_64F).var()
            sharp_value_intensity = self.sharpness_test(reconstructed_in, hologram.SHAR)

            intensity.append(reconstructed_in)
            sharpness_res.append(sharp_value_intensity)
            diffraction_dis.append(df)

            reconstructed_phase = np.angle(e)
            image_phase.append(reconstructed_phase)

            # TODO: Isolate pd and path name!
        sharpness_data = pd.DataFrame({"Sharpness_intensity": sharpness_res, "diffraction distance": diffraction_dis})
        sharpness_data.to_excel(str('./result/' + 'Sharpness' + str(term) + '.xls'), engine='openpyxl')
        intensity = np.squeeze(intensity)
        # print('intensity shape ' + str(np.shape(intensity)))

        return sharpness_res, diffraction_dis, image_phase, intensity

    def angular_mask(self, image, vector, delta, rec_scale):
        a = np.fft.fftshift(np.fft.fft2(image))
        n_x, m_y = a.shape
        extent_x = m_y * delta
        extent_y = n_x * delta
        kx = np.linspace(-np.pi * m_y // 2 / (extent_x / 2), np.pi * m_y // 2 / (extent_x / 2), m_y)
        ky = np.linspace(-np.pi * n_x // 2 / (extent_y / 2), np.pi * n_x // 2 / (extent_y / 2), n_x)

        kx, ky = np.meshgrid(kx, ky)

        kz = np.sqrt(vector ** 2 - kx ** 2 - ky ** 2)
        mask = (vector ** 2 - kx ** 2 - ky ** 2) > 0
        return a, kz, mask, n_x, m_y

    def reconstruction_angular(self, holo, image, volume):
        fft_img, kz, mask, n_x, m_y = self.angular_mask(image, holo.vector, holo.delta, holo.rec_scale)

        sharpness_second, diffraction_dis_2, image_phase_stack, intensity_2 = self.angular_spectrum(holo, fft_img, kz,
                                                                                                    mask,
                                                                                                    2, holo.rec_scale,
                                                                                                    holo.rec_pos,
                                                                                                    holo.expansion_main,
                                                                                                    volume)
        index_img_max = np.argmax(sharpness_second)
        distance = diffraction_dis_2[index_img_max]

        phase_result = image_phase_stack[index_img_max]
        intensity_result = intensity_2[index_img_max]

        return phase_result, distance, intensity_result, intensity_2

    def background_unit(self, img):
        img = img - gaussian(img, sigma=150)
        histogram, bin_edges = np.histogram(img, bins=256)
        max_histogram = bin_edges[np.argmax(histogram)]
        image_back = img - max_histogram
        return image_back
