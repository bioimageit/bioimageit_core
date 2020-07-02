
import os
import imageio
import numpy as np


def sim_content(image1: str, image2: str):
    """Compare if image1 and image2 have same content

    The comparison is made using the mean square error.

    Returns
    -------
    true if the images have the same content, false otherwise

    """
    np_image1 = imageio.imread(image1)
    np_image2 = imageio.imread(image2)
    MSE = np.square(np.subtract(np_image1,np_image2)).mean()
    if MSE < 0.001:
        return True
    return False    