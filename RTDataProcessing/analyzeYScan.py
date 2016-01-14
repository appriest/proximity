import numpy as np
import matplotlib.pyplot as plt
import pixieBinParser as pbp

from scipy.optimize import curve_fit

from mpl_toolkits.mplot3d import Axes3D
from matplotlib.collections import PolyCollection

def analyzeData(plot3d=False, strip=0, plotPeaks=True):

    import os

    fileDir = os.getcwd() + '/data/'

    allEvents = None

    verts = []
    zs = list(np.arange(0,1.85,0.05))

    fileList = os.listdir(fileDir)
    fileList.sort()

    peakPos0 = []
    peakPos1 = []
    peakPos2 = []
    peakPos3 = []
    peakPos4 = []
    peakPos5 = []
    peakPos6 = []
    peakPos7 = []

    verts0 = []
    verts1 = []
    verts2 = []
    verts3 = []
    verts4 = []
    verts5 = []
    verts6 = []
    verts7 = []

    fig = plt.figure()
    ax = fig.gca()

    colors=['blue','red','green','magenta','orange','gold','sage','gray']

    p0 = [100.,600.,20.]

    peakStart = 80
    peakEnd = 140

    for fileNum,thisFile in enumerate(fileList):

        if fileNum > 36:

            break

        if thisFile[-4:] == '.bin':

            print "Reading ", thisFile, "..."

            path = fileDir + '/' + thisFile

            eventArray = readData(filePath=path)

            ys0,bins = np.histogram([event[0] for event in eventArray['pulseHeights']]
                    ,bins=151,range=(100.,1000.))
            ys0[0],ys0[-1] = 0,0
            verts0.append(list(zip(bins[:-1],ys0)))
            peakPos0.append(bins[np.argmax(ys0[-70:]) + 81])
            bin_centres = (bins[:-1] + bins[1:])/2
            coeff0,varMat0 = fitGauss(bin_centres[peakStart:peakEnd], 
                    ys0[peakStart:peakEnd], fileNum, 0, ax)

            ys1,bins = np.histogram([event[1] for event in eventArray['pulseHeights']]
                    ,bins=151,range=(100.,1000.))
            ys1[0],ys1[-1] = 0,0
            verts1.append(list(zip(bins[:-1],ys1)))
            peakPos1.append(bins[np.argmax(ys1[-70:]) + 81])
            bin_centres = (bins[:-1] + bins[1:])/2
            coeff1,varMat1 = fitGauss(bin_centres[peakStart:peakEnd], 
                    ys1[peakStart:peakEnd], fileNum, 1, ax)

            ys2,bins = np.histogram([event[2] for event in eventArray['pulseHeights']]
                    ,bins=151,range=(100.,1000.))
            ys2[0],ys2[-1] = 0,0
            verts2.append(list(zip(bins[:-1],ys2)))
            peakPos2.append(bins[np.argmax(ys2[-70:]) + 81])
            bin_centres = (bins[:-1] + bins[1:])/2
            coeff2,varMat2 = fitGauss(bin_centres[peakStart:peakEnd], 
                    ys2[peakStart:peakEnd], fileNum, 2, ax)
            
            ys3,bins = np.histogram([event[3] for event in eventArray['pulseHeights']]
                    ,bins=151,range=(100.,1000.))
            ys3[0],ys3[-1] = 0,0
            verts3.append(list(zip(bins[:-1],ys3)))
            peakPos3.append(bins[np.argmax(ys3[-70:]) + 81])
            bin_centres = (bins[:-1] + bins[1:])/2
            coeff3,varMat3 = fitGauss(bin_centres[peakStart:peakEnd], 
                    ys3[peakStart:peakEnd], fileNum, 3, ax)

            ys4,bins = np.histogram([event[4] for event in eventArray['pulseHeights']]
                    ,bins=151,range=(100.,1000.))
            ys4[0],ys4[-1] = 0,0
            verts4.append(list(zip(bins[:-1],ys4)))
            peakPos4.append(bins[np.argmax(ys4[-70:]) + 81])
            bin_centres = (bins[:-1] + bins[1:])/2
            coeff4,varMat4 = fitGauss(bin_centres[peakStart:peakEnd], 
                    ys4[peakStart:peakEnd], fileNum, 4, ax)

            ys5,bins = np.histogram([event[5] for event in eventArray['pulseHeights']]
                    ,bins=151,range=(100.,1000.))
            ys5[0],ys5[-1] = 0,0
            verts5.append(list(zip(bins[:-1],ys5)))
            peakPos5.append(bins[np.argmax(ys5[-70:]) + 81])
            bin_centres = (bins[:-1] + bins[1:])/2
            coeff5,varMat5 = fitGauss(bin_centres[peakStart:peakEnd], 
                    ys5[peakStart:peakEnd], fileNum, 5, ax)

            ys6,bins = np.histogram([event[6] for event in eventArray['pulseHeights']]
                    ,bins=151,range=(100.,1000.))
            ys6[0],ys6[-1] = 0,0
            verts6.append(list(zip(bins[:-1],ys6)))
            peakPos6.append(bins[np.argmax(ys6[-70:]) + 81])
            bin_centres = (bins[:-1] + bins[1:])/2
            coeff6,varMat6 = fitGauss(bin_centres[peakStart:peakEnd], 
                    ys6[peakStart:peakEnd], fileNum, 6, ax)

            ys7,bins = np.histogram([event[7] for event in eventArray['pulseHeights']]
                    ,bins=151,range=(100.,1000.))
            ys7[0],ys7[-1] = 0,0
            verts7.append(list(zip(bins[:-1],ys7)))
            peakPos7.append(bins[np.argmax(ys7[-70:]) + 81])
            bin_centres = (bins[:-1] + bins[1:])/2
            coeff7,varMat7 = fitGauss(bin_centres[peakStart:peakEnd], 
                    ys7[peakStart:peakEnd], fileNum, 7, ax)
    
    if plot3d:
        poly0 = PolyCollection(verts0)

        poly0.set_alpha(0.4)

        fig3d = plt.figure()

        ax3d = fig.gca(projection='3d')

        ax3d.add_collection(poly0, zs=zs, zdir='y')

        ax3d.set_xlabel('Energy Bin (ADC units)')
        ax3d.set_ylabel('Counts')

        ax3d.set_xlim3d(0,1000)
        ax3d.set_ylim3d(0,1.85)
        ax3d.set_zlim3d(0,300)

    ax.set_xlabel('Source Position (in)')
    ax.set_ylabel('Peak Position (ADC units)')
    plt.show()

    return [peakPos0, peakPos1, peakPos2, peakPos3, peakPos4, peakPos5, \
            peakPos6, peakPos7]

def readData(filePath = None):

            prsr = pbp.pixieParser(fname=filePath,
                    moduleNum=2,
                    channelNum=[4,4])
            prsr.readBinFile()
            eventArray = prsr.makeAndWriteEvents()
            return eventArray

def gauss(x, A, mu, sigma):
    return A*np.exp(-(x-mu)**2/(2.*sigma**2))
            
def fitGauss(xdata, ydata, posNum, channel, axis):
    try:
        coeffs, varMat = curve_fit(gauss, xdata, ydata, posNum)
        axis.errorbar(0.05*posNum,coeffs[1],yerr=varMat[1,1],marker='o',mfc=colors[channel])

    except:
        print "Unable to fit the peak for position number ", posNum
        coeffs, varMat = 0,0

    return coeffs, varMat

if __name__ == "__main__":

    analyzeData()
