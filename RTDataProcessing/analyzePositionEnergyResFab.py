import calibrationClass as cc
import numpy as np
import pixieBinParser as pp
from pyqtgraph import QtGui,QtCore
import time
import os
from scipy.optimize import curve_fit
from plotBox import plotBox
import matplotlib.pyplot as plt
from numpy import random

def analyzeData(cal=None,plotAll=True,remapX=False):

    if cal == None:
        cal = cc.calibration(minHeight=0,moduleNum=2,channelNum=[4,4])
        cal.callParser(folderName='fabricatedData')
        cal.reconstructWP()
        cal.energyCalibration()

    print "\n\nDone reading file... \n\n"

    curDir = os.getcwd()
    fileDir = curDir + '/fabricatedData/'

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

    for i,thisFile in enumerate(fileList):

        filePath = fileDir + thisFile
        print "Reconstructing events from: ", filePath
        prsr = pp.pixieParser(fname=filePath,moduleNum=2,
                channelNum=[4,4])
        if thisFile[-3:] == 'bin':
            prsr.readBinFile()
        else:
            prsr.readTextFile()
        eventList = prsr.makeAndWriteEvents()
        if prsr.goodEvents <= 50:
            continue

        positions = []
        energies = []

        for event in eventList:

            if event['isGood'] and event['ratioMain']<20.:
                x,E = cal.mapEvent(event)

                if event['regionMain']%2 == 0:
                    positions.append(x + (np.argmax(event['pulseHeights'])-1.)*cal.stripPitch)
                else:
                    positions.append(np.argmax(event['pulseHeights'])*cal.stripPitch - x)

                energies.append(E)
        
        posHist, bins = np.histogram(positions,bins=900,range=(0.,30.))

        for binCounts in posHist:
            if binCounts == 0:
                binCounts = random.rand()

        xbinCenters = np.array((bins[:-1] + bins[1:]))/2.

        xbins.append(list(xbinCenters))
        posHists.append(list(posHist))

        if max(posHist)>10:
            try:
                fit, cov = fitGauss(list(xbinCenters),list(posHist),isX=True)
                xFits.append([fit,cov])
            except:
                print "Could not fit position histogram."

        EHist, EBin = np.histogram(energies,bins=500,range=(0.,100.))

        EbinCenters = np.array((EBin[:-1] + EBin[1:]))/2.

        Ebins.append(list(EbinCenters))
        EHists.append(list(EHist))
    
        if max(EHist)>10:
            try:
                fit, cov = fitGauss(list(EbinCenters),list(EHist))
                EFits.append([fit,cov])
            except:
                print "Could not fit energy histogram."

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

def plotDiff(diff=None,boxOffset=0.):

    if diff is None:
        print "Please provide the diff..."
        return 1

    ax = plotBox(vert=max(diff)+max(diff)/10.,offset=boxOffset)

    ax.errorbar(xAct,diff,yerr=stdDevs,marker='o')
    ax.plot(xAct,np.zeros(len(diff)),'k-')

    plt.xlabel('Position (mm)')
    plt.ylabel('Deviation from linear (mm)')

def calcDiff(xFits,err=False):

    xAct = np.arange(len(xFits))*0.127
    xs = np.array([fit[0][1] for fit in xFits])
    if err:
        stdDevs = np.array([fit[1] for fit in xFits if len(fit)>1])
        stdDevs = np.array([cov[2] for cov in stdDevs if len(cov)>2])
        stdDevs = np.array([cov[2] for cov in stdDevs if len(cov)>2])

    diff = np.array([x-f for x,f in zip(xs,xAct[::-1] if not np.isnan(x) 
        and not np.isinf(x))])
    diff = diff - np.ones(len(diff))*np.average(diff)

    return [diff,xAct]

def plotAllEs(EHists,Ebins):

    fig = plt.figure()

    ax = fig.add_subplot(111)

    EHistAll = list(np.sum(EHists,axis=0))

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

def plotHists(posHists,xbins,xFits,numList=None):

    from plotSourcePos import plotSourcePos
    diff,xAct = calcDiff(xFits)

    ax = plotBox(vert=100,regionLines=True)
    #ax = plotSourcePos(ax,numList,diff=diff)

    for num in numList:

        ax.step(xbins[num],posHists[num])

    for tick in ax.xaxis.get_major_ticks():
        tick.label.set_fontsize(16)
    for tick in ax.yaxis.get_major_ticks():
        tick.label.set_fontsize(16)

    plt.xlabel('Position (mm)',fontsize=16)
    plt.ylabel('Counts',fontsize=16)

def compareWPs(wpfbasename,cal):

    from writeEventFiles import readWPFile

    ax = plotBox(vert=1.0)

    for i in range(1,7):

        wpfname = wpfbasename+str(i)+'.fld'
        pos,WP = readWPFile(wpfile=wpfname)
        maxWP = max(WP)
        pos = [p*1000-27.95+2.5 for p in pos]
        ax.plot(pos,WP,'k--')

    cal.maxWP = maxWP
    cal.reconstructWP()

    for i,WP in enumerate(cal.WP):
        if i%2==0:
            ax.plot(np.linspace(i*2.5,(i+1)*2.5,len(WP)),WP)
        else:
            ax.plot(np.linspace(i*2.5,(i+1)*2.5,len(WP)),WP[::-1])

    plt.xlabel('Position (mm)', fontsize=16)
    plt.ylabel('Weighting Potential', fontsize=16)
    plt.title('Weighting Potential Comparison After WP Reconstruction')
