import csv
import os
import matplotlib.pyplot as plt
import numpy as np
from scipy import ndimage, signal
from scipy.stats import linregress, norm

def PBCorrect(img):
    # loc = "./kymograph35.tif"
    # img = ndimage.imread(loc, flatten = True)

    #Approximate photobleaching as linear process on 1-min timescale
    rs = np.mean(img, 1)
    t = np.linspace(0, len(rs)-1, len(rs))
    #print(t)
    slope, intercept, r_value, p_value, std_err = linregress(t, rs)

    plt.figure("RowSum before pb-correction")
    plt.plot(t, rs)
    plt.plot(t, intercept + t*slope)

    #Invert photobleaching effect
    #y = mx + b
    #x = (y-b)/m
    img2 = img
    for i in range(0, img.shape[0]):
        for j in range(0, img.shape[1]):
            img2[i][j] = (img2[i][j] - i * slope)

    rs2 = np.mean(img,1)
    plt.figure("RowSum after pb-correction")
    plt.plot(t, rs2)

    plt.figure("Images")
    plt.subplot(121), plt.imshow(img, cmap = 'gray'), plt.title("original")
    plt.subplot(122), plt.imshow(img2, cmap = 'gray'), plt.title("corrected")
    #plt.show()
    return(img2)
