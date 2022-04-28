##DHM_utils
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

def read_local(path_name, background_file_name, hologram_file_name):
    hologram_raw = plt.imread(str(path_name + '/Data_10x/' + hologram_file_name + '.tiff'))  # read the file
    hologram_raw = np.array(hologram_raw[:, :], dtype=float)  # reads first channel
    background_read = plt.imread(str(path_name + '/Data_10x/' + background_file_name + '.tiff'))
    background_read = np.array(background_read[:, :], dtype=float)

    return hologram_raw, background_read


# def ROI_apply(img1, top, bot, left, right):
#     img1 = img1[left: right, top: bot]
#     return img1


def Hanning_filter(m_x, n_y, c_x, c_y, r):
    r = int(r * 1.3)

    hann = np.sqrt(np.outer(np.hanning(r * 2), np.hanning(r * 2)))
    hann = np.pad(hann, ((int(c_x - r), int(m_x - c_x - r)), (int(c_y - r), int(n_y - c_y - r))), 'constant')

    return hann


def fourier_process(img_pre, filter_pre):
    fourier_pre = np.fft.fft2(img_pre)
    fourier_selected = np.fft.ifftshift(np.fft.fftshift(fourier_pre) * filter_pre)
    fourier_selected = np.fft.ifft2(fourier_selected)

    return fourier_selected


def Apodization_process(img, k_factor=1.5):
    l0x, l0y = img.shape
    l0x = l0x - (expansion * 3)
    l0y = l0y - (expansion * 3)

    holo = np.pad(img, pad_width=expansion, mode='edge')
    lx, ly = holo.shape

    ax = - (np.pi / 2) * (lx - l0x) / (l0x - lx + 2)
    bx = (np.pi / 2) * (lx + l0x + 2) / (lx - l0x - 2)
    ay = - (np.pi / 2) * (ly - l0y) / (l0y - ly + 2)
    by = (np.pi / 2) * (ly + l0y + 2) / (ly - l0y - 2)

    wx = Flat_window(lx, l0x, ax, bx, k_factor)
    wy = Flat_window(ly, l0y, ay, by, k_factor)

    x, y = np.meshgrid(wy, wx)

    window = x * y

    img_processed = holo * window

    return img_processed

def Sharpness_test(img):
    img = background_unit(img)
    img_gaussian = gaussian(img, sigma=1)

    fourier = np.fft.fftshift(np.fft.fft2(np.abs(img_gaussian)))
    sharp = np.sum(np.log(1 + abs(fourier)))
    # n_img, m_img = img.shape

    # sharp = np.sum(np.square(np.absolute(img) - np.mean(img_gaussian))) / (n_img * m_img)
    # sharp = cv2.Laplacian(img_gaussian, cv2.CV_64F).var()
    shar.append(img)
    return sharp

def Angular_spectrum(img_res, n_x, m_y, kz, mask, term, scale, pos, vol):
    image_phase = []
    intensity = []
    sharpness_res = []
    diffraction_dis = []
    gaussian_img = []

    bar_first = tqdm(range(1, vol))

    for z in bar_first:
        bar_first.set_description("Processing_Angular " + str(term) + ":" + str(int(z + 1)))
        df = pos + z * scale / vol
        c = np.where(mask, img_res * np.exp(1j * kz * df), 0)
        e = np.fft.ifft2(np.fft.ifftshift(c))
        e = e[expansion: expansion + m, expansion: expansion + n]

        reconstructed_in = np.real(e * np.conjugate(e))
        # sharp_value_intensity = cv2.Laplacian(reconstructed_in, cv2.CV_64F).var()
        sharp_value_intensity = Sharpness_test(reconstructed_in)

        intensity.append(reconstructed_in)
        sharpness_res.append(sharp_value_intensity)
        diffraction_dis.append(df)

        reconstructed_phase = np.angle(e)
        image_phase.append(reconstructed_phase)

    sharpness_data = pd.DataFrame({"Sharpness_intensity": sharpness_res, "diffraction distance": diffraction_dis})
    sharpness_data.to_excel(str(path_name + '/Result/' + 'Sharpness' + str(term) + '.xls'), engine='openpyxl')
    intensity = np.squeeze(intensity)
    # print('intensity shape ' + str(np.shape(intensity)))

    return sharpness_res, diffraction_dis, image_phase, intensity


def Angular_mask(image, vector, delta):
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


def Reconstruction_Angular(image, V):
    fft_img, kz, mask, n_x, m_y = Angular_mask(image)
    sharpness_second, diffraction_dis_2, image_phase_stack, intensity_2 = Angular_spectrum(fft_img, n_x, m_y, kz, mask,
                                                                                           2, rec_scale, rec_pos, V)
    index_img_max = np.argmax(sharpness_second)
    distance = diffraction_dis_2[index_img_max]

    phase_result = image_phase_stack[index_img_max]
    intensity_result = intensity_2[index_img_max]

    return phase_result, distance, intensity_result, intensity_2


def background_unit(img):

    img = img - gaussian(img, sigma=150)
    histogram, bin_edges = np.histogram(img, bins=256)
    max_histogram = bin_edges[np.argmax(histogram)]
    image_back = img - max_histogram
    return image_back