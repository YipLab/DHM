import plotly.graph_objects as go
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
from matplotlib import cm
from scipy import interpolate
import pandas as pd
import seaborn as sns
import tifffile as tf
import os
import numpy as np
import napari
import pandas as pd

# Read data from a csv
x = 3.45
y = x
magnification = 15.28
h_divider = x / magnification

Height = tf.imread('../../Example Images/result_height_angle_1.tiff')
 
# xx, yy = np.mgrid[0:Height.shape[0]* h_divider, 0:Height.shape[1]* h_divider]




def pad_to_square(a, pad_value=0):
  m = a.reshape((a.shape[0], -1))
  padded = pad_value * np.ones(2 * [max(m.shape)], dtype=m.dtype)
  padded[0:m.shape[0], 0:m.shape[1]] = m
  return padded

z = pad_to_square(Height, 0.)  
# z = Height[0:1900,0:1900]
# # z_data = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/api_docs/mt_bruno_elevation.csv')
x, y = np.linspace(0, 1, z.shape[0]), np.linspace(0, 1, z.shape[1])
f = interpolate.interp2d( x, y, z, kind='cubic' )
xi, yi = np.meshgrid(x, y)
zi = f( x, y )
# # x, y = np.arange(0,z.shape[0] * h_divider), np.arange(0,z.shape[1] * h_divider)
# fig = go.Figure(data=[go.Surface(z=z, x=x, y=y)])
# fig.update_layout(title='Mt Bruno Elevation', autosize=True,
#                   margin=dict(l=65, r=50, b=65, t=90))
# fig.show()



fig = plt.figure()
ax = fig.gca(projection='3d')
ax.set_box_aspect(aspect = (4,4,1))
surf = ax.plot_surface(xi, yi, zi, cmap=cm.magma,
                       linewidth=0, antialiased=False, rcount=200, ccount=200)
ax.set_xlabel('X/\num')
ax.set_ylabel('Y/\num')

fig.set_size_inches(18.5, 10.5, forward=True)
fig.set_dpi(100)
surf.set_clim(-1,5)
fig.colorbar(surf, shrink=0.5, aspect=5)
plt.show()



# vertices = np.array([[0, 0], [0, 20], [10, 0], [10, 10]])
# faces = np.array([[0, 1, 2], [1, 2, 3]])
# values = np.linspace(0, 1, len(vertices))
# surface = (vertices, faces, values)

# viewer = napari.view_surface(surface)  # add the surface







# Get the data (csv file is hosted on the web)
# url = 'https://raw.githubusercontent.com/holtzy/The-Python-Graph-Gallery/master/static/data/volcano.csv'
# data = pd.read_csv(url)

# # Transform it to a long format
# df=data.unstack().reset_index()
# df.columns=["X","Y","Z"]
 
# # And transform the old column name in something numeric
# df['X']=pd.Categorical(df['X'])
# df['X']=df['X'].cat.codes
 
# # to Add a color bar which maps values to colors.
# fig = plt.figure()
# ax = fig.gca(projection='3d')
# surf=ax.plot_trisurf(df['Y'], df['X'], df['Z'], cmap=plt.cm.viridis, linewidth=0.2)
# fig.colorbar( surf, shrink=0.5, aspect=5)
# plt.show()
 



# # Rotate it
# fig = plt.figure()
# ax = fig.gca(projection='3d')
# surf=ax.plot_trisurf(df['Y'], df['X'], df['Z'], cmap=plt.cm.viridis, linewidth=0.2)
# ax.view_init(30, 45)
# plt.show()
 
# # Other palette
# fig = plt.figure()
# ax = fig.gca(projection='3d')
# ax.plot_trisurf(df['Y'], df['X'], df['Z'], cmap=plt.cm.jet, linewidth=0.01)
# plt.show()