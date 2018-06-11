#IFT Kymograph analysis.
#Last update 5/30/2018
#Uses Python V 3.6.1. Not tested on any other version.
#For the sake of version control, runs on "imagePy" virtual environment
#on windows console type: imagePy\Scripts\activate
#Type, deactivate to exit the virtual environment.

#Based on a matlab script by Hiroaki Ishikawa
#This program takes in a kymograph as input, detects IFT trajectories,
#and determines the average speed of the trajectory and average
#intensity of the trajectory.

#Dependencies: matplotlib, numpy, scipy, pandas
#All dependencies are available for free.
import csv
import os
import matplotlib.pyplot as plt
import numpy as np
from scipy import ndimage, signal
from scipy.stats import linregress, norm


def IFTTraj(loc, name):
    #==============
    #File locations
    #==============

    #Location of inpub kymograph
    #loc = "kymograph\kymograph_2\kymograph_2 filtered_forward.tif"

    #Descriptive name. Will become name of folder where results are stored
    #name = "test1"

    filepath = "./Results/" + name
    if(not os.path.isdir(filepath)):
        os.makedirs(filepath)


    #==========
    #Parameters
    #==========
    px_size = 0.104667 #Length of each pixel (um/px)
    fps = 19.33 #Framerate
    range1 = 0.6 #difference range
    sec1 = 2 #input time in seconds for short-time analysis



    #==================
    #Read in kymographs
    #==================
    image_fw01 = ndimage.imread(loc, flatten=True)

    cropend = int(0.9 * len(image_fw01))

    #Crop off the last 100 frames which contain brightfield image
    image_fw01 = image_fw01[0:cropend,]

    #Display image
    fig = plt.figure()
    plt.imshow(ndimage.rotate(image_fw01, angle = 90))
    #plt.show()
    fig.savefig(filepath + "/image.png")

    print("Image read 0 \n")


    #==========================================
    #Determine Flagellar Length and Start point
    #==========================================
    minvalue = 12

    #Flalength
    colsums =[]
    for col in range(0, image_fw01.shape[1]):
        total = 0
        for row in range(0, image_fw01.shape[0]):
            total = total + image_fw01[row][col]
        colsums.append(total/image_fw01.shape[0])

    #Find point from the end where value exceeds threshold
    flapx = int(len(colsums))-1

    # print("Colsums: ", colsums, "\n")
    while(colsums[flapx] < minvalue and flapx > 0):
        flapx = flapx - 1
    if(flapx == 0):
        flapx = int(len(colsums))-1

    #i is now the nth pixel where brightness drops off (where the flagella ends)
    flalength = flapx * px_size

    #Start point
    flastart = 0
    while(colsums[flastart] < minvalue and flastart < int(len(colsums))-1):
        flastart = flastart + 1


    #==========================================
    #Detect IFT trajectory using peak detection
    #==========================================
    #Image smoothing using gaussian filter
    im_fw02 = ndimage.gaussian_filter(image_fw01, sigma = (3,1), order = 0)

    fig = plt.figure()
    plt.imshow(ndimage.rotate(im_fw02, angle = 90))
    #plt.show()
    fig.savefig(filepath + "/smoothimage.png")

    ####Peak Detection
    #Get dimensions of image
    siz_imfw02 = im_fw02.shape
    image_bwfw01 = np.zeros(im_fw02.shape)
    image_kmA1 = np.zeros(im_fw02.shape)

    #Iterate by position (columns) to find peaks
    #In the original code, iteration was by row, but I found that peaks were better defined when itterating by column
    #Recall that the image is an n x m matrix where n = time and m = position
    startpoint = flastart + 5
    PeakInfo1 = [] #List for storing data about each peak
    for x in range(startpoint, siz_imfw02[1]):
        D1 = signal.savgol_filter(im_fw02[:,x],3,1)
        peaks = list(signal.find_peaks_cwt(D1, np.arange(1,10))) #Location of each peak by wavelet method
        peaks = [int(x) for x in peaks] #Convert list of peaks to list of integer indices
        P1 = D1[peaks] #Contains intentisty of each peak
        PE = [[x]*len(peaks), peaks, P1] #List formated as [x position, t position, intensity at (x,t)]
        PeakInfo1.append(PE)
        #plt.plot(D1), plt.scatter(peaks,D1[peaks],color = "red"), plt.show()

        #Recreate image using only peaks
        image_bwfw01[peaks,x] = 1
        image_kmA1[peaks,x] = D1[peaks]
    #
    # #Display image of peaks
    fig = plt.figure()
    plt.subplot(121), plt.imshow(image_bwfw01)
    plt.subplot(122), plt.imshow(image_kmA1)
    #plt.show()
    fig.savefig(filepath + "/peaks.png")

    print("Trajectory detection 0 \n")

    #====================
    #Connect Trajectories
    #====================

    #Collect terms from all bins in PeakInfo1
    import pandas as pd

    AllPeaks = [[],[],[]] #list of lists containing [x, t, intensity]
    for i in range(0,len(PeakInfo1)):
        AllPeaks[0] = AllPeaks[0] + PeakInfo1[i][0]
        AllPeaks[1] = AllPeaks[1] + list(PeakInfo1[i][1])
        AllPeaks[2] = AllPeaks[2] + list(PeakInfo1[i][2])
    AllPeaks = pd.DataFrame(AllPeaks).transpose()

    #Trace trajectories starting from points where x = 0
    #Prepare peak data in single pandas dataframe
    AllPeaks.columns = ['x','t','intensity']
    AllPeaks = AllPeaks.sort_values(by ='t')
    AllPeaks['t'] = pd.to_numeric(AllPeaks['t']).astype('int')

    #Connect points together as single trajectories by a greedy algorithm
    #that takes a starting point, and adds the nearest point within a 20x10 box

    AllTraj = [] #List to store all trajectories in
    for i in range(0, 1):
        p = PeakInfo1[i]
        for j in range(0,len(p[0])):
            point = [p[0][j],p[1][j],p[2][j]] #[x,t,int]
            Traj = [point] #List to store single trajectory in
            AP = AllPeaks

            while(len(AP) > 0 and point[0] < siz_imfw02[1]):
                #Subset AllPeaks to a 20 x 10 box around the current point
                AP = AllPeaks[(AllPeaks['t'] > point[1] - 10) & (AllPeaks['t'] < point[1]+10) & (AllPeaks['x'] > point[0]) & (AllPeaks['x'] < point[0] + 10)]

                if(len(AP) > 0):
                    #Find nearest point
                    dist = (AP['x']-point[0])**2 + (AP['t']-point[1])**2
                    ind = dist.idxmin()
                    point = AllPeaks.loc[ind]
                    Traj.append(list(point))
            # Traj = pd.DataFrame(Traj)
            # plt.plot(Traj[0], Traj[1]), plt.show()
            # print(Traj)
            AllTraj.append(pd.DataFrame(Traj))
    #print(len(AllTraj))

    # #Plot trajectories
    # for i in range(0,len(AllTraj)):
    #     plt.plot(AllTraj[i][1],AllTraj[i][0]) #X = time, y = pos
    # plt.show()

    #Check trajectories exist on original image. Seems to work
    image_bwfw02 = np.zeros(im_fw02.shape)
    #print(AllTraj[0])
    for i in range(0,len(AllTraj)):
        for index, row in AllTraj[i].iterrows():
            image_bwfw02[int(row[1]),int(row[0])] = 1

    # plt.subplot(131), plt.imshow(image_bwfw02), plt.title("Detected Trajectories")
    # plt.subplot(132), plt.imshow(image_bwfw01), plt.title("Real Trajectories")
    # plt.subplot(133), plt.imshow(image_fw01), plt.title("Original image")
    # plt.show()

    print("Trajectories connected 0 \n")

    #====================
    #Filter Trajectories
    #====================

    #Calculate average number of points in each trajectory
    total = 0
    for i in range(0,len(AllTraj)):
        total = total + len(AllTraj[i])
    avg = total//len(AllTraj)

    #Only keep trajectories with above average number of points
    FilterTraj1 = [] #List to contain filtered trajectories
    for i in range(0, len(AllTraj)):
        if(len(AllTraj[i]) >= avg//2):
            FilterTraj1.append(AllTraj[i])

    print("Filtering 0 \n")

    #===================
    #Calculate IFT speed
    #===================
    #Here I assume that IFT speed = dX/dT where x is position and t is time
    #To calculate speed, I do a linear least squares regression on each trajectory

    TrajLines = [] #List to hold information for each trajectory
    #Each entry is formated as below:
        #(slope, intercept, rvalue, pvalue, stderr)

    #Recall FilterTraj1 is a list of the form [x,t,int]
    for i in range(0, len(FilterTraj1)):
        l = linregress(FilterTraj1[i][1], FilterTraj1[i][0]) #x = time, y = pos
        TrajLines.append(l)

    TrajLines2 = pd.DataFrame(TrajLines) #Slopes in terms of pixel coordinates
    TrajSpeed = TrajLines2['slope']*px_size*fps #Converted from pixel coordinate system to spaciotemporal coordinates


    #Fit slopes to normal distribution
    parameters = norm.fit(TrajSpeed)
    x = np.linspace(0,4,100)
    fittedpdf = norm.pdf(x, loc = parameters[0], scale = parameters[1])
    averageslope = parameters[0]

    # #plot histogram of slopes
    fig = plt.figure()

    plt.subplot(121)
    for i in range(0,len(FilterTraj1)):
        plt.plot(FilterTraj1[i][1]/fps,FilterTraj1[i][0]*px_size) #X = time, y = pos
    plt.xlabel("Time (s)")
    plt.ylabel("Position (um)")
    plt.title("Isolated Trajectories")

    plt.subplot(122)
    plt.hist(TrajSpeed, normed = True, alpha = 0.3, color = 'blue')
    plt.plot(x, fittedpdf, color = 'red')
    plt.text(0,0.5, "mean = " + str(round(parameters[0],2)) + " um/s")
    plt.xlabel("Slope (um/s)")
    plt.title("Distribution of IFT speeds")
    #plt.show()
    fig.savefig(filepath + "/trajectories.png")

    print("Calculate IFT speed 0 \n")

    #=======================
    #Calculate IFT Intensity
    #=======================
    #Using image_kmA1
    #Sum all points in the image and divide by time to find avg intensity
    #at any given time point
    tintensity = 0 #To hold total intensity
    for i in range(0, image_kmA1.shape[0]): #Where shape is (time, pos)
        for j in range(0, image_kmA1.shape[1]):
            tintensity = tintensity + image_kmA1[i][j]


    #Define avgintensity = totalintensity/number of sampled timepoints
    avgintensity = tintensity/(image_kmA1.shape[0])

    #Calculate avg intensity for each trajectory.
    trajintensity = []
    for i in range(0, len(FilterTraj1)):
        trajintensity.append(sum(FilterTraj1[i][2])/len(FilterTraj1[i][2]))

    print("Calculate IFT intensity 0 \n")

    #===========
    #Export Data
    #===========
    #Export average trajectory speed and intensity for each trajectory
    Results1 = [list(TrajSpeed), trajintensity]
    Results1 = pd.DataFrame(Results1).transpose()
    Results1.columns = ['speed', 'intensity']
    Results1.to_csv(filepath + "/Results1.csv")

    #Export number of analyzed trajectories, average speed, average intensity
    Summary1 = pd.DataFrame([len(FilterTraj1), averageslope, avgintensity]).transpose()
    Summary1.columns = ['n', 'avgSpeed','avgIntensity']
    Summary1.to_csv(filepath + "/Summary1.csv")

    Data = [name, len(FilterTraj1), averageslope, avgintensity, flalength]
    #Export data to shared document
    if(not os.path.isfile("Data.csv")):
        with open(r"Data.csv",'a') as f:
            writer = csv.writer(f)
            writer.writerow(['Sample','numTraj','avgSlope','avgInt', 'flalength'])

    with open(r"Data.csv", 'a') as f:
        writer = csv.writer(f)
        writer.writerow(Data)

    #Close plots
    plt.close("all")

    print("Data exported 0 \n")
