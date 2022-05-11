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


# def ROI_apply(img1, top, bot, left, right):
#     img1 = img1[left: right, top: bot]
#     return img1


def hanning_filter(m_x, n_y, c_x, c_y, r):
    hann = np.sqrt(np.outer(np.hanning(r * 2), np.hanning(r * 2)))
    hann = np.pad(hann, ((int(c_x - r), int(m_x - c_x - r)), (int(c_y - r), int(n_y - c_y - r))), 'constant')
    return hann


def fourier_process(img_pre, filter_pre):
    fourier_pre = np.fft.fft2(img_pre)
    fourier_selected = np.fft.ifftshift(np.fft.fftshift(fourier_pre) * filter_pre)
    fourier_selected = np.fft.ifft2(fourier_selected)

    return fourier_selected


def flat_window(l_end, l_begin, a, b, k_fac):
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


def apodization_process(img, k_factor, expansion):
    l0x, l0y = img.shape
    l0x = l0x - (expansion * 3)
    l0y = l0y - (expansion * 3)

    holo = np.pad(img, pad_width=expansion, mode='edge')
    lx, ly = holo.shape

    ax = - (np.pi / 2) * (lx - l0x) / (l0x - lx + 2)
    bx = (np.pi / 2) * (lx + l0x + 2) / (lx - l0x - 2)
    ay = - (np.pi / 2) * (ly - l0y) / (l0y - ly + 2)
    by = (np.pi / 2) * (ly + l0y + 2) / (ly - l0y - 2)

    wx = flat_window(lx, l0x, ax, bx, k_factor)
    wy = flat_window(ly, l0y, ay, by, k_factor)

    x, y = np.meshgrid(wy, wx)

    window = x * y

    img_processed = holo * window

    return img_processed


def sharpness_test(img, shar):
    img = background_unit(img)
    img_gaussian = gaussian(img, sigma=1)

    fourier = np.fft.fftshift(np.fft.fft2(np.abs(img_gaussian)))
    sharp = np.sum(np.log(1 + abs(fourier)))
    # n_img, m_img = img.shape

    # sharp = np.sum(np.square(np.absolute(img) - np.mean(img_gaussian))) / (n_img * m_img)
    # sharp = cv2.Laplacian(img_gaussian, cv2.CV_64F).var()
    shar.append(img)
    return sharp


# in continuous mode, should not use Angular
def angular_spectrum(hologram, img_res, kz, mask, term, recon_scale, recon_start, expansion, vol):
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
        sharp_value_intensity = sharpness_test(reconstructed_in, hologram.SHAR)

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


def angular_mask(image, vector, delta, rec_scale):
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


def reconstruction_angular(holo, image, volume):
    fft_img, kz, mask, n_x, m_y = angular_mask(image, holo.vector, holo.delta, holo.rec_scale)

    sharpness_second, diffraction_dis_2, image_phase_stack, intensity_2 = angular_spectrum(holo, fft_img, kz, mask,
                                                                                           2, holo.rec_scale,
                                                                                           holo.rec_pos,
                                                                                           holo.expansion_main,
                                                                                           volume)
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
