import calibrationClass as cc
import numpy as np
import pixieBinParser as pp
from pyqtgraph import QtGui,QtCore
import pyqtgraph as pg
import time
import os
from scipy.optimize import curve_fit
from plotBox import plotBox
import matplotlib.pyplot as plt

def analyzeData(cal=None,plotAll=True,remapX=False):

    if cal == None:
        cal = cc.calibration()
        cal.callParser(folderName='xdata')
        cal.reconstructWP()
        cal.energyCalibration()

    print "\n\nDone reading file... \n\n"

    curDir = os.getcwd()
    fileDir = curDir + '/xdata/'

    fileList = os.listdir(fileDir)
    fileList.sort()

    ECurves = []
    posCurves = []
    
    xbins = []
    posHists = []
    Ebins = []
    EHists = []

    xFits = []
    EFits = []

    for i,thisFile in enumerate(fileList[21:-22]):

        filePath = fileDir + thisFile
        print "Reconstructing events from: ", filePath
        prsr = pp.pixieParser(fname=filePath,moduleNum=2,
                channelNum=[4,4])
        prsr.readBinFile()
        eventList = prsr.makeAndWriteEvents()

        positions = []
        energies = []

        '''
        r4Events = []
        r7Events = []
        r3Events = []
        '''

        for event in eventList:

            if event['isGood'] and event['ratioMain']<20.:
                x,E = cal.mapEvent(event)

                '''
                if i not in range(135,158) and event['regionMain'] == 4:
                    r4Events.append(E)
                elif i not in range(77,98) and event['regionMain'] == 7:
                    r7Events.append(E)
                elif i not in range(157,176) and event['regionMain'] == 3:
                    r3Events.append(E)
                '''

                if event['regionMain']%2 == 0:
                    positions.append(x + (np.argmax(event['pulseHeights'])-1.)*cal.stripPitch)
                else:
                    positions.append(np.argmax(event['pulseHeights'])*cal.stripPitch - x)

                energies.append(E)
            
        
        
        posHist, bins = np.histogram(positions,bins=1000,range=(0.,30.))

        xbinCenters = np.array((bins[:-1] + bins[1:]))/2.

        xbins.append(list(xbinCenters))
        posHists.append(list(posHist))

        fit, cov = fitGauss(list(xbinCenters),list(posHist),isX=True)
        xFits.append([fit,cov])

        EHist, EBin = np.histogram(energies,bins=500,range=(0.,100.))

        EbinCenters = np.array((EBin[:-1] + EBin[1:]))/2.

        Ebins.append(list(EbinCenters))
        EHists.append(list(EHist))
    
        fit, cov = fitGauss(list(EbinCenters),list(EHist))
        EFits.append([fit,cov])

    if remapX:

        diff,xAct = plotDiff(xFits,returnDiff=True)
        cal.adjustMap(diffs=diff,diffXs=xAct)
        cal.reconstructWP()
        cal.energyCalibration()
        xbins,posHists,Ebins,EHists,xFits,EFits,cal = analyzeData(cal=cal,plotAll=False)
    
    if plotAll:
        plotDiff(xFits)
        plotAllEs(EHists,Ebins)
        plotAllXs(posHists,xbins)
        plt.show()

    return xbins,posHists,Ebins,EHists,xFits,EFits,cal
    #fileLoop(ECurves,posCurves,fileList)

def fitGauss(xdata, ydata, isX=False):

    numSum = 0.
    denSum = 0.
    
    centroid = 0.
    deviation = 0.

    xstep = xdata[-1]-xdata[-2]
    lastx = xdata[-1]
    firstx = xdata[0]

    maxBin = np.argmax(ydata)

    for i in range(20):

        xdata.append(lastx+xstep*(i+1))
        ydata.append(0)
        xdata.reverse()
        ydata.reverse()
        xdata.append(firstx-xstep*(i+1))
        ydata.append(0)
        xdata.reverse()
        ydata.reverse()

    if (xdata[maxBin] > 50. and xdata[maxBin] < 70.) or isX:
        for x1,Ebin1 in zip(list(xdata[maxBin-15:maxBin+16]), 
                list(ydata[maxBin-15:maxBin+16])):
            numSum += x1*Ebin1
            denSum += Ebin1

        if denSum is not 0.:
            centroid = numSum/denSum
        else:
            centroid = 0.
    
        numSum = 0.

        if denSum is not 0.:
            for x2,Ebin2 in zip(list(xdata[maxBin-15:maxBin+16]),
                    list(ydata[maxBin-15:maxBin+16])):
                numSum += Ebin2 / denSum * (centroid-x2)**2.

        deviation = np.sqrt(numSum)

    try:
        fit,var = curve_fit(gauss,xdata,ydata,p0=[50,centroid,deviation])
    except:
        print "Fit failed..."
        fit=[np.max(ydata),centroid,deviation]
        var=np.zeros((3,3))

    if fit[2]<0:
        fit[2] = -fit[2]
    elif fit[2]>5 and not isX:
        try:
            fit,var = curve_fit(gauss,xdata[50:70],ydata[50:70],
                    p0=[50,centroid,deviation])
        except:
            print "Fit failed..."
            fit=[np.max(ydata),centroid,deviation]
            var=np.zeros((3,3))
    elif fit[2]>0.5 and isX:
        try:
            i = round(centroid/30.*1000.)
            fit,var = curve_fit(gauss,xdata[i-15:i+16],ydata[i-15:i+16],
                    p0=[50,centroid,deviation])
        except:
            print "Fit failed..."
            fit=[np.max(ydata),centroid,deviation]
            var=np.zeros((3,3))

    return fit,var

def gauss(x,A,mu,sig):
    return A*np.exp(-((x-mu)**2)/(2.*sig**2))

def plotDiff(xFits,boxOffset=0.,returnDiff=False):

    xAct = np.arange(len(xFits))*0.127
    xs = np.array([fit[0][1] for fit in xFits])
    stdDevs = np.array([fit[1] for fit in xFits])
    stdDevs = np.array([cov[2] for cov in stdDevs])
    stdDevs = np.array([cov[2] for cov in stdDevs])

    diff = np.array([x-f for x,f in zip(xs,xAct[::-1])])
    diff = diff - np.ones(len(diff))*np.average(diff)

    ax = plotBox(vert=max(diff)+max(diff)/10.,offset=boxOffset)

    ax.errorbar(xAct,diff,yerr=stdDevs,marker='o')
    ax.plot(xAct,np.zeros(len(diff)),'k-')

    plt.xlabel('Position (mm)')
    plt.ylabel('Deviation from linear (mm)')

    if returnDiff:

        return [diff,xAct]

def plotAllEs(EHists,Ebins):

    fig = plt.figure()

    ax = fig.add_subplot(111)

    EHistAll = np.sum(EHists,axis=0)

    fit,var = fitGauss(Ebins[0],EHistAll)

    Es = np.linspace(0,100,1000)
    fitCurve = gauss(Es,fit[0],fit[1],fit[2])

    ax.plot(Ebins[0],EHistAll,'k')
    ax.plot(Es,fitCurve,'r--')

    plt.xlabel('E (keV)')
    plt.ylabel('Counts')

    print 'Centroid (keV):  ',fit[1]
    print '\nFWHM (keV):  ', fit[2]*2.355

def plotAllXs(posHists,xbins):

    ax = plotBox(vert=1000,regionLines=True)

    plt.xlabel('Position (mm)')
    plt.ylabel('Counts')

    xhistAll = np.sum(posHists,axis=0)

    ax.plot(xbins[0],xhistAll,'k')

def plotHists(posHists,xbins,numList=None):

    ax = plotBox(vert=100,regionLines=True)

    for num in numList:

        ax.plot(xbins[num],posHists[num])

    plt.xlabel('Position (mm)')
    plt.ylabel('Counts')

def fileLoop(ECurves,posCurves,fileList):

    app = QtGui.QApplication([])

    win = pg.GraphicsWindow(title="Mapping Position and Energy Resolution")
    win.resize(1000,600)
    win.setWindowTitle('Mapping Position and Energy Resolution')

    posPlot = win.addPlot(title="Position Histogram")
    posPlot.setLabel('left',"Counts")
    posPlot.setLabel('bottom',"Position (mm)")

    EPlot = win.addPlot(title="Energy Histogram")
    EPlot.setLabel('left',"Counts")
    EPlot.setLabel('bottom',"Energy (keV)")

    global paused
    paused = False

    while win.isVisible():
        for i,f in enumerate(fileList):

            time.sleep(0.5)
                
            posPlot.clear()
            EPlot.clear()

            posPlot.addItem(posCurves[i])
            posPlot.setTitle(f+" Position Histogram")

            EPlot.addItem(ECurves[i])
            EPlot.setTitle(f+" Energy Histogram")

            time.sleep(0.5)

            import sys
            if(sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
                QtGui.QApplication.instance().exec_()
