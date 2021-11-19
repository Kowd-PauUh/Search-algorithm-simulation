"""
Created by Ivan Danylenko
Date 11.11.21
"""

from PIL import Image
import numpy as np
from matplotlib import cm
from matplotlib import pyplot as plt

fig, ax = plt.subplots(subplot_kw={"projection": "3d"})

im = Image.open('Heightmaps/heightmap40.jpg', 'r')
im = im.transpose(Image.FLIP_TOP_BOTTOM)
width, height = im.size
pixel_values = list(im.getdata())
pixel_alpha = []
z = []

# 0, 1, 2, 3
# 4, 5, 6, 7
# 8, 9, 10, 11

for pixel in pixel_values:
    pixel_alpha.append(round(pixel[0], 3))

for i in range(0, len(pixel_alpha), width):
    z.append(pixel_alpha[i:i+width])

x = np.arange(width)
y = np.arange(height)
x, y = np.meshgrid(x, y)
z = np.array(z)

surf = ax.plot_surface(x, y, z, cmap=cm.coolwarm,
                       linewidth=0, antialiased=False)
plt.show()
