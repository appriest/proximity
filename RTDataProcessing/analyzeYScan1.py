import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import pixieBinParser as pbp

from scipy.optimize import curve_fit

from mpl_toolkits.mplot3d import Axes3D
from matplotlib.collections import PolyCollection
import os

mpl.rcParams['font.family']='cmr10'

def analyzeData(plot3d=True, strips=[], plotPeaks=True, fitPeaks=True):

    fileDir = os.getcwd() + '/ydata/'
    fileList = os.listdir(fileDir)
    fileList.sort()

    allEvents = None

    verts = [[],[],[],[],[],[],[],[]]

    zs = list(np.arange(len(fileList))*1.27)

    
    centroids = []
    stdDevs = []
    for i in range(len(strips)):
        centroids.append([])
        stdDevs.append([])

    colors = ['black', 'blue', 'green', 'red', 'cyan', 'magenta', 'yellow', 
            'burlywood', 'chartreuse', 'gray', 'darkorange', 'olive', 'sienna']

    numBins=201

    for fileNum,thisFile in enumerate(fileList):

        if fileNum > 35:

            break

        elif fileNum < 3:

            continue

        if thisFile[-4:] == '.bin':

            print "Reading ", thisFile, "..."

            path = fileDir + '/' + thisFile

            eventArray = readData(filePath=path)

            for strip in strips:

                ys,bins = np.histogram([event[strip] for event in eventArray['pulseHeights']]
                        ,bins=numBins,range=(100.,1000.))
                ys[0],ys[-1] = 0,0
                verts[strip].append(list(zip(bins[:-1],ys)))
                peakPos = np.argmax(ys[-70:]) + 81
                if fitPeaks:
                    bin_centres = (bins[:-1] + bins[1:])/2
                    peakStart = peakPos-10
                    peakEnd = peakPos+10
                    centroid,stdDev = fitGauss(bin_centres[peakStart:peakEnd], 
                            ys[peakStart:peakEnd])
                    centroids[strip].append(centroid)
                    stdDevs[strip].append(stdDev)
                    ax.errorbar(zs[fileNum],centroid/centroids[strip][0],
                            yerr=stdDev/centroids[strip][0],
                            ecolor=colors[strip],marker='o',mfc=colors[strip])

