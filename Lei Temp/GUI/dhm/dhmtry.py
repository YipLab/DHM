import numpy as np
from tkinter.filedialog import askdirectory
import tifffile as tf
from tqdm import tqdm
import matplotlib.pyplot as plt
import numpy as np
from tkinter.filedialog import askdirectory
import tifffile as tf
from tqdm import tqdm
import matplotlib.pyplot as plt
import math
import pandas as pd
from skimage.filters import gaussian
from skimage.restoration import unwrap_phase  # intall 'Microsoft's vcredist_x64.exe' if it not work

path_name = askdirectory()
focus_result = pd.DataFrame({})

focus = [24.0, 23.0, 26.0, 27.0]

num = 0
# for file in range(2, 5):
#   focus_result.insert(num, 'file', focus)
#  num += 1
focus_result.insert(num, 'file', focus)
print(focus_result)
focus_result.to_excel(
    str(path_name + '/' + str(234) + '.xls'),
    engine='openpyxl')
