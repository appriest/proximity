import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import pixieBinParser as pbp

from scipy.optimize import curve_fit

from mpl_toolkits.mplot3d import Axes3D
from matplotlib.collections import PolyCollection

mpl.rcParams['font.family']='cmr10'

def analyzeData(plot3d=True, strips=0, plotPeaks=True, fitPeaks=True):

    import os

    fileDir = os.getcwd() + '/ydata/'

    fileList = os.listdir(fileDir)
    fileList.sort()

    allEvents = None

    verts = [[],[],[],[],[],[],[],[]]

    zs = list(np.arange(len(fileList))*1.27)

    centroids = [[],[],[],[],[],[],[],[]]
    stdDevs = [[],[],[],[],[],[],[],[]]

    fig = plt.figure()
    ax = fig.gca()

    colors=['blue','red','green','magenta','orange','gold','black','gray']

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

    ax.set_xlim(-0.05,1.9)
    ax.set_ylim(0.85,1.25)
    ax.set_xlabel('Source Position (in)')
    ax.set_ylabel('Peak Position (ADC units)')
    
    if plot3d:
        poly = PolyCollection(verts[strips[0]])

        poly.set_alpha(0.4)

        fig3d = plt.figure()

        ax3d = fig.gca(projection='3d')

        ax3d.add_collection3d(poly, zs=zs, zdir='y')

        ax3d.set_xlabel('Energy Bin (ADC units)')
        ax3d.set_ylabel('Counts')

        ax3d.set_xlim3d(0,1000)
        ax3d.set_ylim3d(0,50)
        ax3d.set_zlim3d(0,300)

    plt.show()

    return [centroids,stdDevs]

def plotData(centroids,stdDevs,strips=None):

    colors=['blue','red','green','magenta','orange','gold','black','gray']
    fig = plt.figure()
    ax = fig.add_subplot(111)

    if strips == None:
        for i,stripCentroids in enumerate(centroids):
            for j,centroid in enumerate(stripCentroids):
                centroid = centroid/stripCentroids[0]
                ax.errorbar(j*1.27,centroid,yerr=stdDevs[i][j]/stripCentroids[0],
                        marker='x',ecolor=colors[i],color=colors[i])

    else:
        for strip in strips:
            for j,centroid in enumerate(centroids[strip]):
                centroid = centroid/centroids[strip][0]
                ax.errorbar(j*1.27,centroid,yerr=stdDevs[strip][j]/centroids[strip][0],
                        marker='x',ecolor=colors[strip],color=colors[strip])

    plt.xlabel('Position Along Strip Length (mm)')
    plt.ylabel('Normalized Peak Position')

    ax.set_xlim((-0.5,j*1.27+0.5))
    ax.set_ylim((0.85,1.25))

    plt.show()

def readData(filePath = None):

            prsr = pbp.pixieParser(fname=filePath,
                    moduleNum=2,
                    channelNum=[4,4])
            prsr.readBinFile()
            eventArray = prsr.makeAndWriteEvents()
            return eventArray

def gauss(x, A, mu, sigma):
    return A*np.exp(-(x-mu)**2/(2.*sigma**2))
            
def fitGauss(xdata, ydata):

    numSum = 0.
    denSum = 0.
    
    centroid = 0.
    deviation = 0.

    for x1,Ebin1 in zip(list(xdata), list(ydata)):
        numSum += x1*Ebin1
        denSum += Ebin1

    centroid = numSum/denSum
    
    numSum = 0.

    for x2,Ebin2 in zip(list(xdata),list(ydata)):
        numSum += Ebin2 * (centroid-x2)**2./denSum

    deviation = np.sqrt(numSum)
        
 
    return centroid, deviation

if __name__ == "__main__":

    analyzeData(strips=range(8))
