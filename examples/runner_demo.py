import os
from skimage.io import imread
import matplotlib.pyplot as plt
import bioimageit_core.api as iit

# First we connect to the database (here it is a local database)
req = iit.Request('./config_sample.json')
req.connect()

print('- Get a specific tool from it name and version')
tool = req.get_tool('spitfiredeconv2d_v0.1.2')
if tool:
    print('    Tool found')
    print('- Print the spitfiredeconv2d_v0.1.2 man page:')
    tool.man()

# run the tool on an image
req.exec(tool,
         i='tests/test_images/data/population1_001.tif',
         o='population1_001_deconv.tif',
         sigma=4,
         regularization=12,
         weighting=0.1,
         method='SV',
         padding=True)

# visualize the output
out_image = imread('population1_001_deconv.tif')
plt.figure()
plt.imshow(out_image)
plt.show()

# delete the result file
os.remove('population1_001_deconv.tif')
