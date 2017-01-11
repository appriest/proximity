import numpy as np
import scipy as sp
from eventClass import event
import matplotlib.pyplot as plt
import matplotlib as mpl
from lmfit import Model
from plotBox import plotBox

# Change matplotlibs default font to courier for this script
mpl.rcParams['font.family']='cmr10'

colors = ['black', 'blue', 'green', 'red', 'cyan', 'magenta', 'yellow', 
            'burlywood', 'chartreuse', 'gray', 'darkorange', 'olive', 'sienna']

class calibration:

    def __init__(self, calType = 0, stripPitch = 5., numBins = 2000, \
                 moduleNum=2, channelNum=[4,4], numWPbins = 500,
                 maxWP = 0.75, minHeight=15., channelConfig = None):

        '''Usage: calibration(calType=0,stripPitch=5.,numBins=2000,numStrips=8)

        calType(int): Meant for implementing different kinds of reconstruction
            methods. Only "method 2" is currently implemented. Others will
            follow.
        stripPitch(float): Use float/double type in mm.
        numBins(int): Indicates the number of bins to be used in the ratio
            histograms. This will also dictate the granularity of the position-
            ratio mapping.
        numStrips(int): Use integer type.

        This class is for storing and manipulating data that can be used for
        reconstructing data from a proximity type detector of a certain
        geometry. More info to come.'''

        self.notes = ""
        self.calType = calType
        self.moduleNum = moduleNum
        self.channelNum = channelNum
        self.numStrips = sum(self.channelNum)
        self.numBins = numBins
        self.stripPitch = stripPitch
        self.numEvents = np.zeros(self.numStrips*2-4)
        self.rhist = np.zeros((self.numStrips*2-4,self.numBins))
        self.mapping = np.zeros((self.numStrips*2-4, self.numBins))
        self.numWPbins = numWPbins
        self.numGoodEvents = 0
        self.numBadEvents = 0
        self.maxWP = maxWP
        self.energyCal = np.ones((self.numStrips*2-4))
        self.minHeight = minHeight
        self.channelConfig = channelConfig

        self.dt = np.dtype([('pulseHeights',np.int32,(self.numStrips,)),
                ('regionMain',np.int8),
                ('regionSec',np.int8),
                ('ratioMain',np.float64),
                ('ratioSec',np.float64),
                ('t',np.uint32),
                ('x',np.float32),
                ('E',np.float64),
                ('isGood',np.bool_)])

        #self.allEvents = np.ndarray((0,),dtype=self.dt)
        self.allEvents = []

        self.goodEvents = np.ndarray((0,),dtype=self.dt)

    def addEvents(self, eventArray = None):

        ''' Usage: addEvent(eventArray = None)

            Provide a numpy masked array with the dtype matching the dtype defined
            in this object. '''

        if eventArray is None or eventArray.dtype != self.dt:

            print "You did not provide a valid array! \n\n"

        else:

            for event in eventArray:

                self.allEvents.append(event)

                check1 = np.floor(event['ratioMain']*100.)<self.numBins-1
                check2 = event['ratioMain']>=1.
                #check3 = np.argmax(event['pulseHeights'])
                check4 = np.max(event['pulseHeights'])>self.minHeight

                if check1 and check2 and check4 and event['isGood']:

                    region = event['regionMain']
                    
                    ratioBin = np.floor(event['ratioMain']*100.)

                    self.rhist[region][ratioBin] += 1

                    self.numGoodEvents += 1

                    self.numEvents[region] += 1

                else:

                    self.allEvents[-1]['isGood'] = False
                    self.numBadEvents += 1

    def callParser(self,fname=None,folderName=None):

        '''
        File: calibrationClass.py
        Author: Anders Priest
        Description: Use this function to load raw data from binary files,
            either from a single file or from a set of files from a directory.
            If a directory name is given, all .bin files from that directory
            will be loaded, and other files will be ignored. If the name of a
            file and the name of a folder are given, this will result in an
            error. The specified folder must be in the current working
            directory.
        '''

        if fname is not None and folderName is not None:

            print "You cannot provide both a file name and a folder name!\n"
            return 1

        import pixieBinParser as pp

        if fname is not None:

            print "Reading ", fname, "..."
            prsr = pp.pixieParser(fname=fname,moduleNum=self.moduleNum,
                                  channelNum=self.channelNum, 
                                  minHeight=self.minHeight,
                                  channelConfig=self.channelConfig)

            if fname[-3:] == 'bin':
                prsr.readBinFile()
            else:
                prsr.readTextFile()

            eventList = prsr.makeAndWriteEvents()

            self.addEvents(eventList)

            print "Done!\n"

        elif folderName is not None:

            import os

            curDir = os.getcwd()

            fileDir = curDir + '/' + folderName

            eventList = []

            fileList = os.listdir(fileDir)
            fileList.sort()

            for thisFile in fileList:

                if thisFile[-4:] == '.bin' or thisFile[-4:] == '.txt':

                    print "Reading ", thisFile, "..."
                    prsrPath = folderName + '/' + thisFile
                    prsr = pp.pixieParser(fname=prsrPath,
                                         moduleNum=self.moduleNum,
                                         channelNum=self.channelNum,
                                         minHeight=self.minHeight,
                                         channelConfig=self.channelConfig)
                    if thisFile[-3:] == 'bin':
                        prsr.readBinFile()
                    else:
                        prsr.readTextFile()
                    eventList = prsr.makeAndWriteEvents()

                    self.addEvents(eventList)

                    del prsr
                    print "Done!\n"

                else:

                    print "Skipping ", thisFile, ", because it is not a .bin or .txt file..."

            print "Done!\n"

        else:

            print "You didn't specify anything!\n"
            return 1

        self.updateMap()

    def updateMap(self):

        '''Usage: updateMap()

        Integrates over the ratio histograms for each region creating the
        mapping from ratio to position.
        
        *** Does not need event type update. *** '''

        # Updates the mapping from ratio to position
        # Performs an integral on the histograms for each of the regions

        print "Updating map plot...\n"

        self.mapping = np.array([[sum(subArray[0:i+100])/self.numEvents[j] \
                                  for i,ratio in enumerate(subArray[100:])] \
                                 for j,subArray in enumerate(self.rhist)])

        self.mapping = self.mapping*self.stripPitch/2.

    def adjustMap(self,diffs=None,diffXs=None):

        if diffs == None or diffXs == None:

            return 0

        else:

            for region,mapping in enumerate(self.mapping):

                for i,oldMap in enumerate(mapping):

                    oldMapX = region*2.5+oldMap

                    approxBin = int(round(oldMapX/0.127))-5

                    for j,actX in enumerate(diffXs[approxBin:]):
                        if oldMapX<actX:
                            j = j+approxBin
                            break

                    diff = (diffs[j]-diffs[j-1])/(diffXs[j]-diffXs[j-1])* \
                            (oldMapX-diffXs[j-1])+diffs[j-1]

                    if oldMap+diff<=2.5 and oldMap+diff>0.:

                        self.mapping[region][i] = oldMap + diff

                    elif oldMap+diff<0.:

                        self.mapping[region][i] = oldMap

                    else:

                        self.mapping[region][i] = 2.5

    def plotMap(self, regions = None):

        '''Usage: plotMap(region = None)

        region(int): If region is provided, only the mapping for the region
            provided will be mapped. Otherwise, all regions will be plotted.

        Simply plots the mapping for the region given or for all regions.

        *** Does not need event type update. *** '''

        if regions == None:

            # Plots the current mapping between ratio and position for all
            # regions

            print "Plotting map for all regions...\n"

            fig = plt.figure()
            ax = fig.add_subplot(111)

            ratioX = np.linspace(1.,20.,num=1900)

            for region, ratioMap in enumerate(self.mapping):

                lineName = "  Region " + str(region)
                ax.plot(ratioMap,ratioX,
                        label=lineName, color=colors[region])

            # Shrink current axis's height by 10% on the bottom
            box = ax.get_position()
            ax.set_position([box.x0, box.y0 + box.height * 0.1,
                                 box.width * 0.9, box.height * 0.9])

            plt.ylabel('Ratio',fontsize=16)
            plt.xlabel('Position within region',fontsize=16)

            plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))

            for tick in ax.xaxis.get_major_ticks():
                tick.label.set_fontsize(16)
            for tick in ax.yaxis.get_major_ticks():
                tick.label.set_fontsize(16)

            plt.show()

        else:

            # Plots the current mapping between ratio and position for the
            # region listed

            print "Plotting map for regions ", regions, "...\n"

            fig = plt.figure()
            ax = fig.add_subplot(111)

            ratioX = np.linspace(1.,20.,num=1900)

            for i,region in enumerate(regions):
                lineName = "  Region " + str(region)
                ax.plot(self.mapping[region,:],ratioX,label=lineName,
                        color=colors[i])

            # Shrink current axis's height by 10% on the bottom
            box = ax.get_position()
            ax.set_position([box.x0, box.y0 + box.height * 0.1,
                                 box.width * 0.9, box.height * 0.9])

            plt.ylabel('Ratio',fontsize=16)
            plt.xlabel('Position within region',fontsize=16)

            plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))

            for tick in ax.xaxis.get_major_ticks():
                tick.label.set_fontsize(16)
            for tick in ax.yaxis.get_major_ticks():
                tick.label.set_fontsize(16)

            plt.show()

    def plotHist(self, regions = None):

        '''Usage: plotHist(region = None)

        region(int): Region to be plotted. If None, plots all regions.

        Plots the current ratio histograms for the regions.

        *** Does not need event type update. *** '''

        if regions == None:

            # Plot all regions

            print "Plotting ratio histogram for all regions...\n"

            fig = plt.figure()
            ax = fig.add_subplot(111)

            for i,hist in enumerate(self.rhist):

                x = np.linspace(0,len(hist)/100.,len(hist))
                histName = "  Region " + str(i)
                ax.plot(x,hist, label=histName, color=colors[i])

            # Shrink current axis's height by 10% on the bottom
            box = ax.get_position()
            ax.set_position([box.x0, box.y0 + box.height * 0.1,
                                 box.width * 0.9, box.height * 0.9])

            plt.ylabel('Counts',fontsize=16)
            plt.xlabel('Pulse Height Ratio',fontsize=16)

            plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))

            for tick in ax.xaxis.get_major_ticks():
                tick.label.set_fontsize(16)
            for tick in ax.yaxis.get_major_ticks():
                tick.label.set_fontsize(16)

            plt.show()

        else:

            # Plot the region listed

            print "Plotting ratio histogram for region", regions, "...\n"

            fig = plt.figure()
            ax = fig.add_subplot(111)

            for i,region in enumerate(regions):

                x = np.linspace(0,len(self.rhist[region])/100.,len(self.rhist[region]))
                histName = "  Region " + str(region)
                ax.plot(x,self.rhist[region,:], label=histName, 
                        color=colors[i])

            # Shrink current axis's height by 10% on the bottom
            box = ax.get_position()
            ax.set_position([box.x0, box.y0 + box.height * 0.1,
                                 box.width * 0.9, box.height * 0.9])

            plt.ylabel('Counts',fontsize=16)
            plt.xlabel('Pulse Height Ratio',fontsize=16)

            plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))

            for tick in ax.xaxis.get_major_ticks():
                tick.label.set_fontsize(16)
            for tick in ax.yaxis.get_major_ticks():
                tick.label.set_fontsize(16)

            plt.show()

    def reconstructWP(self):

        '''
        File: calibrationClass.py
        Author: Anders Priest
        Description: Loops through event positions and max pulseheights,
            generates a pulseheight histogram for each position and finds the
            centroid, which is then saved as the WP for that position. The WPs
            are then normalized by the max height and multiplied by a factor
            equal to the measured max WP height.
        '''

        print "Reconstructing weighting potentials from the calibration data..."

        self.WP = np.zeros((self.numStrips*2-4,
            int(np.ceil(50.*self.stripPitch/2.+1))))
        self.WPmask = np.zeros((self.numStrips*2-4,
            int(np.ceil(50.*self.stripPitch/2.+1))))
        self.wpReconstructHist = np.zeros((self.numStrips*2-4,
            int(np.ceil(50.*self.stripPitch/2.+1)),200))
        wpReconOrg = []
        for i in range(self.numStrips*2-4):
            wpReconOrg.append([])
            for j in range(int(np.ceil(50.*self.stripPitch/2.)+1)):
                wpReconOrg[i].append([])
        binEdges = np.arange(0,1001,4)
        binCenters = (binEdges[:-1] + binEdges[1:])/2.

        for e in self.allEvents:

            if e['isGood'] and max(e['pulseHeights'])>self.minHeight: # and \
                    #max(e['pulseHeights'])<1000:

                e['x'] = self.mapEvent(e = e, xOnly = 1)
            
                wpReconOrg[e['regionMain']][int(round(e['x']*50.))].append(
                    max(e['pulseHeights']))

                '''if max(e['pulseHeights']) < 1000:
                    for thisBin,edge in enumerate(binEdges):
                        if max(e['pulseHeights'])<edge:
                            break

                    self.wpReconstructHist[e['regionMain']][round(e['x']*50.)]\
                        [thisBin-1] += 1'''

        for region,regionArray in enumerate(wpReconOrg):
            for pos,posArray in enumerate(regionArray):
                self.wpReconstructHist[region][pos],binEdges = np.histogram(posArray,
                    bins=200,range=(0.,2000.))

        for i,region in enumerate(self.wpReconstructHist):

            for j,histAtPosition in enumerate(region):
                
                if sum(histAtPosition) > 1000:

                    peakPos = np.argmax(histAtPosition[25:])+25
                    #peakPos = sum([height*(peak-15+bin_) for bin_,height 
                    #    in enumerate(histAtPosition[peak-15:peak+16])])/ \
                    #            sum(range(peak-15,peak+16))
                    
                    #peakPos = np.argmax(histAtPosition[15:])+15
                
                    self.WP[i][j] = peakPos

                else:

                    peakPos = np.argmax(histAtPosition[25:])+25
                    #peakPos = sum([height*(peak-15+bin_) for bin_,height 
                    #    in enumerate(histAtPosition[peak-15:peak+16])])/ \
                    #            sum(range(peak-15,peak+16))

                    #reakPos = np.argmax(histAtPosition[15:])+15

                    self.WP[i][j] = peakPos

                    self.WPmask[i][j] = 1

        for region,WP_r in enumerate(self.WP):
            self.WP[region] = WP_r/max(WP_r)*self.maxWP

        self.WPx = [num*self.stripPitch/2./len(self.WP[0]) 
            for num in range(len(self.WP[0]))]

        print "Done!"

    def plotWPs(self, plotStrips=True):

        if plotStrips:
            ax = plotBox(stripPitch=self.stripPitch,stripNum=sum(self.channelNum),
                    stripWidth=stripWidth)
        else:
            fig = plt.figure()
            ax = fig.add_subplot(111)

        # Plotting the weighting potentials across space

        for region,wp_r in enumerate(self.WP):
            WPname = " Region " + str(region)
            if region % 2 == 0:
                ax.plot(np.linspace(0,self.stripPitch/2.,
                        len(wp_r))+np.ones((len(wp_r)))*region*self.stripPitch/2.,wp_r,
                        label=WPname, color=colors[region])
            else:
                ax.plot(np.linspace(0,self.stripPitch/2.,
                        len(wp_r))+np.ones((len(wp_r)))*region*self.stripPitch/2.,wp_r[::-1],
                        label=WPname, color=colors[region])

        # Shrink current axis's height by 10% on the bottom
        box = ax.get_position()
        ax.set_position([box.x0, box.y0 + box.height * 0.1,
                             box.width * 0.9, box.height * 0.9])

        plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
        plt.ylabel('Weighting Potential',fontsize=16)
        plt.xlabel('Position (mm)',fontsize=16)

        ax.set_ylim([0,1.5])

        for tick in ax.xaxis.get_major_ticks():
            tick.label.set_fontsize(16)
        for tick in ax.yaxis.get_major_ticks():
            tick.label.set_fontsize(16)

        plt.show()

    def writeCalToFile(self, fname = None):

        '''Usage: writeCalToFile(fname = None)

        fname("str"): String literal for the name of the calibration file.

        Implementation has not been written yet. More details to come.'''

        if fname == None:

            print "Please provide a file name!"

        else:

            print "Writing calibration to file: ", fname, "\n"

            # Write calibration

            f = open(fname,wb)

            f.write(self.numStrips)
            f.write(self.stripPitch)
            

            print "...\nFinished!"

    def readCalFromFile(self, fname = None):

        '''Usage: readCalFromFile(fname = None)

        fname("str"): String literal for the file name to read from and store
            into a calibration object.

        Read a saved calibration from a file. Implementation not yet
        written.'''

        if fname == None:

            print "Please provide a file name!"

        else:

            if self.numEvents != 0:

                print "Are you sure you want to overwrite this calibration \
                    object? (Y/N)\n"

                ans = raw_input()

                if 'N' == ans.upper():

                    print "Calibration not overwritten.\n"

                    return 0

                elif 'Y' != ans.upper():

                    print "That isn't a 'Y' or an 'N'. Come on...\n\n"

                    return -1

            # Read a saved calibration from a file into object

            print "Reading calibration from file: ", fname, "\n"

            # Read calibration

            print "...\nFinished!\n"

    def mapEvent(self, e = None, xOnly = 0, EOnly = 0, x = None):

        '''Usage: mapEvent(e = None)

        e(event object): Event instance to be mapped. The event position will
            be added to the attributes of the event instance.

        Take in an event and use the current mapping to reconstruct the
        position of the event

        For the love of god, take the print statements out before trying
        to use this for realsies'''

        if e == None:

            print "Please provide a valid event of class type 'event'!\n"

        else:

            if xOnly == 0 and EOnly == 0:
                xOnly = 1
                EOnly = 1
                both = 1
            elif xOnly == 1 and EOnly == 1:
                both = 1
            else:
                both = 0

            if xOnly == 1:
                index = int(np.floor(e['ratioMain']*100-100))
                if index >= self.numBins-101:
                    e['x'] = 2.5
                else:
                    e['x'] = (self.mapping[e['regionMain']][index+1]- \
                            self.mapping[e['regionMain']][index])* \
                            (e['ratioMain']*100-100-index) + \
                            self.mapping[e['regionMain']][index]

                if both == 0:
                    return e['x']

            if EOnly == 1:
                energy = np.max(e['pulseHeights'])/self.mapXtoWP(e=e) * \
                    self.energyCal

                if both == 0:
                    return energy

            return [e['x'],energy]

    def mapXtoWP(self,e=None):

        '''
        File: calibrationClass.py
        Author: Anders Priest
        Description: Maps position to the reconstructed weighting potential for
            the region where the interaction occurred.
        '''
        if e is not None:
            #return self.WP[e['regionMain'],round(e['x']/ \
            #        self.stripPitch*float(np.shape(self.WP)[1]))]
            for WPbin,WPpos in enumerate(self.WPx):
                if e['x'] < WPpos:
                    break
            return self.WP[e['regionMain']][WPbin]
        
        else:
            print "You need to provide a position to map a weighting potential\
                to!"
            return 0

    def energyCalibration(self):

        print "Using good events to reconstruct the energy calibration..."
        energies = []

        for i,event in enumerate(self.allEvents):

            if event['isGood']:
                event['E'] = self.mapEvent(event,EOnly=1)
                energies.append(event['E'])

        print "The number of events used for this energy calibration: ", len(energies)

        Ehist,EbinEdges = np.histogram(energies,bins=1000,
                range=(0,max(energies)))

        histMax = np.argmax(Ehist)

        self.Ehist,self.EbinEdges = np.histogram(energies,bins=1000,
                range=(0,EbinEdges[histMax+100]))

        histMax = np.argmax(self.Ehist)
        
        self.energyCal = 59.5/((self.EbinEdges[histMax+1]+self.EbinEdges[histMax])/2.)

        self.EbinEdges = self.EbinEdges*self.energyCal

        for i,event in enumerate(self.allEvents):

            if event['isGood']:
                event['E'] = event['E']*self.energyCal

        print "Done!\n\n"

    def plotEnergyCal(self):

        ''' *** Does not need event type update. *** '''

        fig = plt.figure()
        ax = fig.add_subplot(111)

        EbinCenters = (self.EbinEdges[1:]+self.EbinEdges[:-1])/2.
        ax.step(EbinCenters,self.Ehist,color=colors[0])

        # Shrink current axis's height by 10% on the bottom
        box = ax.get_position()
        ax.set_position([box.x0, box.y0 + box.height * 0.1,
                             box.width * 0.9, box.height * 0.9])

        plt.ylabel('Counts',fontsize=16)
        plt.xlabel('Energy (keV)',fontsize=16)

        for tick in ax.xaxis.get_major_ticks():
            tick.label.set_fontsize(16)
        for tick in ax.yaxis.get_major_ticks():
            tick.label.set_fontsize(16)
        
        plt.show()

    def gatherPositions(self,regions=None,fnames=None,xOnly=False,EOnly=False):

        positions = []
        energies = []

        if regions is not None:

            for i,region in enumerate(regions):

                positions.append([])
                energies.append([])

                for event in self.allEvents:

                    if event['isGood'] and event['regionMain'] == region:

                        energies[i].append(event['E'])

                        if event['regionMain']%2 == 0:
                            positions[i].append(event['x'] + 
                                    (np.argmax(event['pulseHeights'])-1.)*self.stripPitch)
                        else:
                            positions[i].append(np.argmax(event['pulseHeights'])*self.stripPitch
                                    - event['x'])

        elif fnames is not None:

            import pixieBinParser as pp
            for i,fileName in enumerate(fnames):

                positions.append([])
                energies.append([])

                filePath = fileName
                prsr = pp.pixieParser(fname=filePath,moduleNum=self.moduleNum,
                        channelNum=self.channelNum,minHeight=self.minHeight,
                                      channelConfig=self.channelConfig)

                if fileName[-3:] == 'bin':
                    prsr.readBinFile()
                elif fileName[0][-3:] == 'txt':
                    prsr.readTextFile()
                else:
                    print 'Skipping: ', fileName
                    continue

                eventList = prsr.makeAndWriteEvents()
                
                for event in eventList:

                    check1 = np.floor(event['ratioMain']*100.) < self.numBins-1
                    check2 = event['ratioMain'] >= 1.

                    if check1 and check2 and event['isGood']:

                        event['x'],event['E'] = self.mapEvent(e=event)

                        energies[i].append(event['E'])

                        if event['regionMain']%2 == 0:
                            positions[i].append(event['x'] + 
                                    (np.argmax(event['pulseHeights'])-1.)*self.stripPitch)
                        else:
                            positions[i].append(np.argmax(event['pulseHeights'])*self.stripPitch
                                    - event['x'])

            if xOnly:
                return positions,eventList
            elif EOnly:
                return energies,eventList
            else:
                return positions,energies,eventList

        else:
            
            for event in self.allEvents:

                if event['isGood']:

                    energies.append(event['E'])

                    if event['regionMain']%2 == 0:
                        positions.append(event['x'] + 
                                (np.argmax(event['pulseHeights'])-1.)*self.stripPitch)
                    else:
                        positions.append(np.argmax(event['pulseHeights'])*self.stripPitch
                                - event['x'])

        if xOnly:
            return positions
        elif EOnly:
            return energies
        else:
            return positions,energies

    def plotPositionHists(self,regions=None,fnames=None,plotE=False,
            stripWidth=1.0,plotStrips=False,vert=120):

        if plotStrips:
            ax = plotBox(stripPitch=self.stripPitch,stripNum=sum(self.channelNum)-2,
                    stripWidth=stripWidth,vert=vert)
        else:
            fig = plt.figure()
            ax = fig.add_subplot(111)

        if plotE:
            fig2 = plt.figure()
            ax2 = fig2.add_subplot(111)

        eventList = None
        
        if regions is not None:

            if plotE:
                positions,energies = self.gatherPositions(regions=regions)
            else:
                positions = self.gatherPositions(regions=regions,xOnly=True)

            for i,region in enumerate(regions):

                histName = "Region " + str(region)

                hist,binEdges = np.histogram(positions[i],bins=1000,
                        range=(0.,self.stripPitch*(sum(self.channelNum)-2)))

                if plotE:
                    Ehist,EbinEdges = np.histogram(energies[i],bins=500,
                            range=(0., 100.))
                    EbinCenters = (EbinEdges[1:]+EbinEdges[:-1])/2.

                binCenters = (binEdges[1:]+binEdges[:-1])/2.
                
                ax.step(binCenters,hist,label=histName,
                        color=colors[i%len(colors)])

                # Shrink current axis's height by 10% on the bottom
                # box = ax.get_position()
                # ax.set_position([box.x0, box.y0 + box.height * 0.1,
                #                     box.width * 0.8, box.height * 0.9])

                plt.ylabel('Counts',fontsize=16)
                plt.xlabel('Position (mm)',fontsize=16)

                for tick in ax.xaxis.get_major_ticks():
                    tick.label.set_fontsize(16)
                for tick in ax.yaxis.get_major_ticks():
                    tick.label.set_fontsize(16)

                if fnames is not None:
                    ncol = np.ceil(len(fnames)/4.)
                else:
                    ncol = 1

                ax.set_ylim(0,max(hist)+max(hist)/5)

                # Put bbox_to_anchor back in if legend outside plot desired
                plt.legend(loc='upper right')   #   , bbox_to_anchor=(1, 0.5)

                if plotE:
                    fig2 = plt.figure()
                    ax2 = fig2.add_subplot(111)
                    ax2.step(EbinCenters,Ehist,label=histName,color=colors[i%len(colors)])
                    plt.xlabel('Energy (keV)')
                    plt.ylabel('Counts')
                    for tick in ax.xaxis.get_major_ticks():
                        tick.label.set_fontsize(16)
                    for tick in ax.yaxis.get_major_ticks():
                        tick.label.set_fontsize(16)

                    self.fitResults = self.fitGauss(xdata = EbinCenters,ydata = Ehist,withBG=True)

                    text2 = 'Gaussian Peak Fitting:\n'
                    text2 += '$\mu$ = ' + str(self.fitResults.best_values['mu']) + ' keV\n'
                    text2 += '$\sigma$ = ' + str(self.fitResults.best_values['sigma']) +' keV\n'
                    text2 += '$BG = $' + str(self.fitResults.best_values['m']) + '$x + $' \
                            + str(self.fitResults.best_values['b'])
                    ax2.text(0.95,0.05,text2,verticalalignment='top',horizontalalignment='left',
                        transform = ax2.transAxes,fontsize=16)

                    plt.legend(loc='upper right')


        elif fnames is not None:

            text = ''
            text2 = ''

            if plotE:
                positions,energies,eventList = self.gatherPositions(fnames=fnames)
            else:
                positions,eventList = self.gatherPositions(fnames=fnames,xOnly=True)

            for i,fileName in enumerate(fnames):

                hist,binEdges = np.histogram(positions[i],bins=1000,
                        range=(0.,self.stripPitch*(sum(self.channelNum)-2)))

                binCenters = (binEdges[1:]+binEdges[:-1])/2.

                self.fitResults = self.fitGauss(binCenters,hist,withBG=False)
                path,fname = fileName.split('/')

                ax.step(binCenters,hist,label=str(i)+', '+fname, 
                        color=colors[i%len(colors)])

                ax.set_ylabel('Counts',fontsize=16)
                ax.set_xlabel('Position (mm)',fontsize=16)

                for tick in ax.xaxis.get_major_ticks():
                    tick.label.set_fontsize(16)
                for tick in ax.yaxis.get_major_ticks():
                    tick.label.set_fontsize(16)

                if fnames is not None:
                    ncol = np.ceil(len(fnames)/4.)
                else:
                    ncol = 1

                text += 'Gaussian Peak Fitting Peak '+ str(i)+ ':\n'
                text += '$\mu$ = ' + str(self.fitResults.best_values['mu']) + ' mm\n'
                text += '$\sigma$ = ' + str(self.fitResults.best_values['sigma']) + ' mm\n'

                if plotE:

                    Ehist,EbinEdges = np.histogram(energies[i],bins=500,
                            range=(0., 100.))
                    EbinCenters = (EbinEdges[1:]+EbinEdges[:-1])/2.
                    ax2.step(EbinCenters,Ehist,label=str(i)+', '+fname,color=colors[i%len(colors)])
                    ax2.set_xlabel('Energy (keV)',fontsize=16)
                    ax2.set_ylabel('Counts',fontsize=16)
                    for tick in ax2.xaxis.get_major_ticks():
                        tick.label.set_fontsize(16)
                    for tick in ax2.yaxis.get_major_ticks():
                        tick.label.set_fontsize(16)

                    self.fitResults = self.fitGauss(xdata = EbinCenters,ydata = Ehist,withBG=True)

                    text2 += 'Gaussian Peak Fitting '+ str(i)+ ':\n'
                    text2 += '$\mu$ = ' + str(self.fitResults.best_values['mu']) + ' keV\n'
                    text2 += '$\sigma$ = ' + str(self.fitResults.best_values['sigma']) +' keV\n'
                    text2 += '$BG = $' + str(self.fitResults.best_values['m']) + '$x + $' \
                            + str(self.fitResults.best_values['b']) + '\n'

            ax.text(0.05,0.95,text,verticalalignment='top',horizontalalignment='left',
                transform = ax.transAxes,fontsize=16)

            handles,labels = ax.get_legend_handles_labels()
            # Put bbox_to_anchor back in if legend outside plot desired
            ax.legend(handles,labels,loc='upper right')   #   , bbox_to_anchor=(1, 0.5)

            if plotE:
                ax2.text(0.05,0.95,text2,verticalalignment='top',horizontalalignment='left',
                    transform = ax2.transAxes,fontsize=16)

                handles,labels = ax2.get_legend_handles_labels()
                ax2.legend(handles,labels,loc='upper right')


        else:

            if plotE:
                positions,energies = self.gatherPositions()
            else:
                positions = self.gatherPositions(xOnly=True)

            hist,binEdges = np.histogram(positions,bins=1000,
                    range=(0.,self.stripPitch*(sum(self.channelNum)-2)))
            
            binCenters = (binEdges[1:]+binEdges[:-1])/2.

            ax.step(binCenters,hist,label="All Events",color=colors[0])
            # Shrink current axis's height by 10% on the bottom
            # box = ax.get_position()
            # ax.set_position([box.x0, box.y0 + box.height * 0.1,
            #                     box.width * 0.8, box.height * 0.9])

            plt.ylabel('Counts',fontsize=16)
            plt.xlabel('Position (mm)',fontsize=16)

            for tick in ax.xaxis.get_major_ticks():
                tick.label.set_fontsize(16)
            for tick in ax.yaxis.get_major_ticks():
                tick.label.set_fontsize(16)

            if fnames is not None:
                ncol = np.ceil(len(fnames)/4.)
            else:
                ncol = 1

            ax.set_ylim(0,max(hist)+max(hist)/5)

            # Put bbox_to_anchor back in if legend outside plot desired
            plt.legend(loc='upper right')   #   , bbox_to_anchor=(1, 0.5)

            if plotE:

                fig2 = plt.figure()
                ax2 = fig2.add_subplot(111)
                Ehist,EbinEdges = np.histogram(energies,bins=500,
                        range=(0., 100.))
                EbinCenters = (EbinEdges[1:]+EbinEdges[:-1])/2.
                ax2.step(EbinCenters,Ehist,label='All Events',color=colors[0])
                plt.xlabel('Energy (keV)',fontsize=16)
                plt.ylabel('Counts',fontsize=16)
                for tick in ax2.xaxis.get_major_ticks():
                    tick.label.set_fontsize(16)
                for tick in ax2.yaxis.get_major_ticks():
                    tick.label.set_fontsize(16)

                    self.fitResults = self.fitGauss(xdata = EbinCenters,ydata = Ehist,withBG=True)

                    text2 = 'Gaussian Peak Fitting:\n'
                    text2 += '$\mu$ = ' + str(self.fitResults.best_values['mu']) + ' keV\n'
                    text2 += '$\sigma$ = ' + str(self.fitResults.best_values['sigma']) +' keV\n'
                    text2 += '$BG = $' + str(self.fitResults.best_values['m']) + '$x + $' \
                            + str(self.fitResults.best_values['b'])
                    ax2.text(0.95,0.05,text2,verticalalignment='top',horizontalalignment='left',
                        transform = ax2.transAxes,fontsize=16)

                plt.legend(loc='upper right')


        plt.show()

        if eventList is not None:
            return positions,eventList

    def fitGauss(self, xdata=None, ydata=None, withBG=False, inits=None):

        '''
        
        Usage: fitGauss(xdata,ydata,withBG=False,inits=None)

        xdata and ydata must have the same length, and a well defined peak

        withBG: fit gaussian with linear background

        inits: withBG == False -> [A,mu,sigma]
               withBG == True  -> [A,mu,sigma,m,b]

        '''
        def gauss(x, A, mu, sigma):
            return A*np.exp(-(x-mu)**2/(2.*sigma**2))
                    
        def gaussBG(x, A, mu, sigma, m, b):
            return b+m*x+A*np.exp(-(x-mu)**2/(2.*sigma**2))

        if withBG:
            gBGmod = Model(gaussBG)
        else:
            gmod = Model(gauss)

        if inits is None:
            mu_i = xdata[np.argmax(ydata)]
            A_i = np.max(ydata)
            sigma_i = 0.5

            if withBG:
                m_i = -0.1
                b_i = ydata[np.argmax(ydata)-50]
        else:
            A_i = inits[0]
            mu_i = inits[1]
            sigma_i = inits[2]
            if withBG:
                m_i = inits[3]
                b_i = inits[4]

        if withBG:
            results = gBGmod.fit(ydata,x=xdata,A=A_i,mu=mu_i,sigma=sigma_i,b=b_i,m=m_i)
        else:
            results = gmod.fit(ydata,x=xdata,A=A_i,mu=mu_i,sigma=sigma_i)

        return results

    def analyzeScan(self, folderName = None, stepSize = None,scanDirec='backward'):

        if folderName is None:
            print 'You need to provide a folder name!\n\n'
            return 0

        import os
        from mpl_toolkits.mplot3d import Axes3D
        from matplotlib.collections import PolyCollection

        posFitResults = []
        EfitResults = []
        xs = []
        xHists = []
        Es = []
        EHists = []
        vertsE = []
        vertsX = []

        curDir = os.getcwd()
        fileDir = curDir + '/' + folderName
        fileList = os.listdir(fileDir)
        fileList.sort()

        for i,thisFile in enumerate(fileList):

            if thisFile[-3:] != 'bin' and thisFile[-3:] != 'txt':
                print 'Skipping: ', thisFile
                continue

            filePath = folderName+thisFile
            path = folderName + '/' + thisFile
            positions,energies,eventList = self.gatherPositions(fnames=[path])

            xHist,xbins = np.histogram(positions,bins=1000,
                    range=(0,self.stripPitch*(sum(self.channelNum)-2)))
            xHist[0],xHist[-1] = 0,0
            xbinCenters = (xbins[:-1]+xbins[1:])/2.
            xs.append(xbinCenters)
            xHists.append(xHist)
            vertsX.append(list(zip(xbinCenters,xHist)))

            EHist,Ebins = np.histogram(energies,bins=200,range=(0,100))
            EHist[0],EHist[-1] = 0,0
            EbinCenters = (Ebins[:-1]+Ebins[1:])/2.
            Es.append(EbinCenters)
            EHists.append(EHist)
            vertsE.append(list(zip(EbinCenters,EHist)))

            posFitResults.append(self.fitGauss(xbinCenters,xHist))
            EfitResults.append(self.fitGauss(EbinCenters,EHist,withBG=True))

        fig3DX = plt.figure()
        fig3DE = plt.figure()
        fig, (ax1,ax2,ax3,ax4) = plt.subplots(4,sharex=True,sharey=False)
        ax4.set_xlabel('Stage Position (mm)',fontsize=16)

        ax3DX = fig3DX.gca(projection='3d')
        ax3DE = fig3DE.gca(projection='3d')

        stageX = np.arange(len(fileList))*stepSize

        polyX = PolyCollection(vertsX,facecolors = colors[0])
        polyX.set_alpha(0.4)
        ax3DX.add_collection3d(polyX,zs=stageX,zdir='y')

        ax3DX.set_ylim((0,self.stripPitch*(sum(self.channelNum)-2)))
        ax3DX.set_xlim((0,self.stripPitch*(sum(self.channelNum)-2)))
        ax3DX.set_zlim((0,max(xHists[len(xHists)/2])+200))

        ax3DX.set_ylabel('Stage Position (mm)',fontsize=16)
        ax3DX.set_xlabel('Extracted Position (mm)',fontsize=16)
        ax3DX.set_zlabel('Counts',fontsize=16)

        polyE = PolyCollection(vertsE,facecolors = colors[0])
        polyE.set_alpha(0.4)
        ax3DE.add_collection3d(polyE,zs=stageX,zdir='y')

        ax3DE.set_ylim((0,self.stripPitch*(sum(self.channelNum)-2)))
        ax3DE.set_xlim((0,100))
        ax3DE.set_zlim((0,max(xHists[len(EHists)/2])+200))

        ax3DE.set_ylabel('Stage Position (mm)',fontsize=16)
        ax3DE.set_xlabel('Extracted Energy (keV)',fontsize=16)
        ax3DE.set_zlabel('Counts',fontsize=16)

        residual = []
        sigma = []
        sigmaErr = []

        energyCent = []
        energyRes = []
        energyResErr = []

        stageXRem = []

        posLimit = self.stripPitch*(sum(self.channelNum)-2)

        for i,fitResults in enumerate(posFitResults):
            if fitResults.best_values['mu']>0 and fitResults.best_values['mu']<posLimit \
                    and fitResults.best_values['sigma']*2.355<1.5:
                stageXRem.append(stageX[i])

                if scanDirec == 'backward':
                    residual.append(fitResults.best_values['mu']-(len(posFitResults)-i)*stepSize)
                else:
                    residual.append(fitResults.best_values['mu']-i*stepSize)
                sigma.append(fitResults.best_values['sigma'])
                sigmaErr.append(fitResults.covar[1][1])

                energyCent.append(EfitResults[i].best_values['mu'])
                energyRes.append(EfitResults[i].best_values['sigma'])
                energyResErr.append(EfitResults[i].covar[3][3])

        residual = residual - np.mean(residual)*np.ones(len(residual))
        stageXRem = stageXRem - np.ones(len(stageXRem))*min(stageXRem)

        print 'Average Position Resolution: ', str(np.mean(sigma)*2.355), ' mm'
        print 'Average Energy Resolution: ', str(np.mean(energyRes)*2.355), ' keV'

        ax1.errorbar(stageXRem,residual,yerr=sigma,color=colors[0])
        ax1.set_ylabel('Extracted\nPosition\nResidual\n(mm)',fontsize=16)
        ax1.set_ylim((-0.5,0.5))
        
        ax2.errorbar(stageXRem,np.array(sigma)*2.355,
                yerr=np.array(sigmaErr)*2.355,color=colors[0])
        ax2.set_ylabel('Position\nResolution\nFWHM\n(mm)',fontsize=16)
        ax2.set_ylim((0,max(sigma)*2.355*1.2))

        ax3.errorbar(stageXRem,energyCent,yerr=energyRes,color=colors[0])
        ax3.set_ylabel('Energy\nCentroid\n(keV)',fontsize=16)
        ax3.set_ylim((0,80))

        ax4.errorbar(stageXRem,np.array(energyRes)*2.355,
                yerr=np.array(energyResErr)*2.355,color=colors[0])
        ax4.set_ylabel('Energy\nResolution\nFWHM\n(keV)',fontsize=16)
        ax4.set_ylim((0,max(energyRes)*2.355*1.5))

        ax4.set_xlim((min(stageXRem),max(stageXRem)))

        plt.show()

    def calProperties(self):

        '''Usage: calProperties()

        Prints the attributes of the calibration object.'''

        print "This calibration object is for a(n) ", self.numStrips, \
            " strip detector.\n"
        print "Strip pitch: ", self.stripPitch, "\n"
        print "Number of events: ", self.numEvents, "\n"
        print "Notes: ", self.notes, "\n\n"

    def addNotes(self, note = None):

        '''Usage: addNotes(note = None)

        note("str"): String literal with the note to be added. note will be
            added onto the end of any existing notes.

        Meant to used for adding additional information about how the
        calibration was constructed (i.e. data used, particular attributes
        used, etc.)'''

        self.notes += " "
        self.notes += note
