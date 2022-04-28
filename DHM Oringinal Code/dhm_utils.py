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


# def ROI_manual_point(img1=None, img2=None):
#     plt.imshow(img1, cmap='gray')  # 8-bit grey scale
#     roi_x = plt.ginput(1)

#     top = np.int(np.subtract(roi_x[0][0], 200))
#     bot = np.int(np.add(roi_x[0][0], 200))
#     left = np.int(np.subtract(roi_x[0][1], 200))
#     right = np.int(np.add(roi_x[0][1], 200))

#     print(roi_x)
#     print(top, bot, left, right)

#     img1 = img1[left: right, top: bot]
#     img2 = img2[left: right, top: bot]
#     plt.imshow(img1, cmap='gray')
#     plt.ginput(1)
#     print('The position of ROI: ', roi_x)
#     return img1, img2, top, bot, left, right


def filter_fixed_point(hologram_raw, quadrant:int=3):
   
	frequency = np.fft.fftshift(np.fft.fft2(hologram_raw))
    m_x, n_y = np.shape(frequency)

    # If First Quadrant
    if quadrant == 1:
	    first_quadrant = frequency[1: int(math.floor(m_x / 2) - 30), int(math.floor(n_y / 2) + 30):n_y - 30]
    	indices = np.where(first_quadrant == np.amax(first_quadrant))

    # If Second Quadrant
	else if quadrant == 2:
	    second_quadrant = frequency[1: int(math.floor(m_x / 2) - 10), 1:int(math.floor(n_y / 2) - 10)]
	    indices = np.where(second_quadrant == np.max(second_quadrant))

    # If Third Quadrant
    else if quadrant == 3:
	    third_quadrant = frequency[int(math.floor(m_x / 2) + 30): m_x - 30, 1:int(math.floor(n_y / 2) - 30)]
	    indices = np.where(third_quadrant == np.amax(third_quadrant))

    # If Fourth Quadrant
	else if quadrant == 4:
	    fourth_quadrant = frequency[int(math.floor(m_x / 2) + 30): m_x - 30, int(math.floor(n_y / 2) + 30):n_y - 30]
	    indices = np.where(fourth_quadrant == np.amax(fourth_quadrant))

    center_x = indices[0]
    center_x = center_x + int(math.floor(m_x / 2) + 30)  # Third Quadrant
    center_y = indices[1]

    distance = np.sqrt(np.power(np.abs(center_x - int(m_x / 2)), 2) + np.power(np.abs(int(n_y / 2) - center_y), 2))
    radius = (distance / 3) * 1.2

    print(center_x, center_y, radius)
    filter_hann = hanning_filter(m_x, n_y, center_x, center_y, radius)

    mesh_m, mesh_n = np.meshgrid(np.arange(0, n_y), np.arange(0, m_x))
    region = np.sqrt((mesh_n - float(center_x)) ** 2 + (mesh_m - float(center_y)) ** 2)
    circle_window = np.array(region <= radius)

    circle_window = circle_window * filter_hann

    plt.imshow(circle_window, cmap='Greys')
    plt.ginput(1)
    return circle_window


def filter_manual_point(hologram_raw):
	frequency = np.fft.fftshift(np.fft.fft2(hologram_raw))
    m_x, n_y = np.shape(frequency)

    center_x = indices[0]
    center_y = indices[1]

    tf.imshow(np.log(1 + abs(frequency)), title="Select A Filter", cmap='gray')
    manual_point = plt.ginput()[0]
    manual_y, manual_x = manual_point
    radius = int(np.sqrt(np.power(center_y - int(manual_y), 2) + np.power(center_x - int(manual_x), 2)))

    print(center_x, center_y, radius)
    filter_hann = Hanning_filter(m_x, n_y, center_x, center_y, radius)

    mesh_m, mesh_n = np.meshgrid(np.arange(0, n_y), np.arange(0, m_x))
    region = np.sqrt((mesh_n - float(center_x)) ** 2 + (mesh_m - float(center_y)) ** 2)
    circle_window = np.array(region <= radius)

    circle_window = circle_window * filter_hann

    plt.imshow(circle_window, cmap='Greys')
    plt.ginput(1)

    return circle_window