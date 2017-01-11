import numpy as np
import os
import matplotlib.pyplot as plt
import pixieBinParser as pp
from lmfit import Model
import matplotlib.pyplot as plt
import matplotlib as mpl

# Change matplotlibs default font to courier for this script
mpl.rcParams['font.family']='cmr10'

colors = ['black', 'blue', 'green', 'red', 'cyan', 'magenta', 'yellow', 
            'burlywood', 'chartreuse', 'gray', 'darkorange', 'olive', 'sienna']

def analyzeYScan(lims=None):

    def gaussexp(x, A, mu, sigma, tau,x0):
        return A*np.exp(-(x-mu)**2/(2.*sigma**2))+np.exp(-(x-x0)/tau)

    if lims == None:
        fstart = 2
        fend = -5
    else:
        fstart = lims[0]
        fend = lims[1]

    path = os.getcwd()
    path += '/ydata/'
    fileList = os.listdir(path)
    fileList.sort()

    maxPHs = []
    results = []
    centroids = [[],[],[],[],[],[],[],[]]
    centUnc = [[],[],[],[],[],[],[],[]]

    for fn in range(len(fileList[fstart:fend])):
        maxPHs.append([])
        results.append([])
        for i in range(8):
            maxPHs[fn].append([])
            results[fn].append([])

    for fileNum, fname in enumerate(fileList[fstart:fend]):

        fpath = path+fname
        prsr = pp.pixieParser(fname=fpath,moduleNum=2,channelNum=[4,4])
        prsr.readBinFile()
        eventlist = prsr.makeAndWriteEvents()

        del prsr

        for event in eventlist:

            maxPHs[fileNum][np.argmax(event['pulseHeights'])].append(max(event['pulseHeights']))

    for fileNum,PHlist in enumerate(maxPHs):

        for stripNum,PHs in enumerate(PHlist):

            hist,binEdges = np.histogram(PHs, bins=40, range = (600,1000))
            binCenters = (binEdges[:-1]+binEdges[1:])/2.

            gmod = Model(gaussexp)

            inits = [50,810,25,250,1500]
            i=0

            while True:
                result = gmod.fit(hist,x=binCenters,A=inits[0],mu=inits[1],
                        sigma=inits[2],tau=inits[3],x0=inits[4])
                i+=1
            
                if result.success:
                    break
                else:
                    if i>10:
                        break
                    inits[1] = binCenters[np.argmax(hist)]
            
            results[fileNum][stripNum] = result

            centroids[stripNum].append(result.best_values['mu'])
            
            if result.success:
                centUnc[stripNum].append(np.sqrt(result.covar[1][1]))
            else:
                centUnc[stripNum].append(0)

    x = np.arange(len(maxPHs))*1.25
    fig, axes = plt.subplots(8,sharex=True,sharey=True)

    for i,data in enumerate(centroids):
        
        axes[i].errorbar(x,data,yerr=centUnc[i],color=colors[0])
        axisLabel = 'Strip ' + str(i) + '\nPeak\nPosition\n(ADC Units)'
        axes[i].set_ylabel(axisLabel,fontsize=16)
    
    axes[-1].set_xlabel('Position Along Strip Length (mm)',fontsize=16)
    plt.show()

    for i in range(8):
        maxCenti = np.max(centroids[i])
        minCenti = np.min(centroids[i])
        maxUnci = centUnc[i][np.argmax(centroids[i])]
        minUnci = centUnc[i][np.argmin(centroids[i])]

        r = maxCenti/minCenti

        var = r*np.sqrt((maxUnci/maxCenti)**2 + (minUnci/minCenti)**2)
        print 'Strip ' + str(i) + ': ' + str(r) + ' +- ' + str(var)

    return centroids,centUnc,results
