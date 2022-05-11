import numpy as np
from tkinter.filedialog import askdirectory
import tifffile as tf
from tqdm import tqdm
import matplotlib.pyplot as plt
import math
# import pandas as pd
from skimage.filters import gaussian
from skimage.restoration import unwrap_phase  # intall 'Microsoft's vcredist_x64.exe' if it not work 
# ( https://docs.microsoft.com/en-us/cpp/windows/latest-supported-vc-redist?view=msvc-170)

import dhm.utils


# ================================= read_local is obsolete , will be removed in the release ==========================
def read_local(path_name, background_file_name, hologram_file_name):
    # def open_file(filepath: str):
    # """Opens a file using the default application."""
    # if _sys.platform.startswith('darwin'):
    #     _subprocess.call(('open', filepath))
    # elif _os.name == 'nt':
    #     _os.startfile(filepath.replace("/", "\\"))  # Windows requires backslashes for network paths like \\server\bla
    # elif _os.name == 'posix':
    #     _subprocess.call(('xdg-open', filepath))

    hologram_raw = plt.imread(str(path_name + hologram_file_name + '.tiff'))  # read the file
    hologram_raw = np.array(hologram_raw[:, :], dtype=float)  # reads first channel
    background_read = plt.imread(str(path_name + background_file_name + '.tiff'))
    background_read = np.array(background_read[:, :], dtype=float)

    return hologram_raw, background_read


# ============================ read_local is obsolete , will be removed in the release =========================#


def filter_fixed_point(hologram_raw, quadrant: str = '1', filter_rate: float = 1.2, filter_type: str = 'Hann'):
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
    radius = (distance / 3) * filter_rate

    mesh_m, mesh_n = np.meshgrid(np.arange(0, shape_horizontal), np.arange(0, shape_vertical))
    region = np.sqrt((mesh_n - float(center_x)) ** 2 + (mesh_m - float(center_y)) ** 2)
    circle_window = np.array(region <= radius)

    if filter_type == "Hann":
        filter_hann = utils.hanning_filter(shape_vertical, shape_horizontal, center_x, center_y, radius)
        circle_window = circle_window * filter_hann

    return circle_window


def filter_manual_point(hologram_raw, indices):
    frequency = np.fft.fftshift(np.fft.fft2(hologram_raw))
    m_x, n_y = np.shape(frequency)

    center_x = indices[0]
    center_y = indices[1]

    tf.imshow(np.log(1 + abs(frequency)), title="Select A Filter", cmap='gray')
    manual_point = plt.ginput()[0]
    manual_y, manual_x = manual_point
    radius = int(np.sqrt(np.power(center_y - int(manual_y), 2) + np.power(center_x - int(manual_x), 2)))

    print(center_x, center_y, radius)
    filter_hann = utils.hanning_filter(m_x, n_y, center_x, center_y, radius)

    mesh_m, mesh_n = np.meshgrid(np.arange(0, n_y), np.arange(0, m_x))
    region = np.sqrt((mesh_n - float(center_x)) ** 2 + (mesh_m - float(center_y)) ** 2)
    circle_window = np.array(region <= radius)

    circle_window = circle_window * filter_hann

    plt.imshow(circle_window, cmap='Greys')
    plt.ginput(1)

    return circle_window
