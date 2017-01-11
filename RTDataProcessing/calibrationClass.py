import numpy as np
import scipy as sp
from eventClass import event
import matplotlib.pyplot as plt
import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtCore
import numpy.ma as ma
import matplotlib.pyplot as plt

class calibration:

    def __init__(self, calType = 0, stripPitch = 5., numBins = 2000, \
                 moduleNum=2, channelNum=[4,4], numWPbins = 500,
                 maxWP = 0.75, minHeight=15.):

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
                                  channelNum=self.channelNum)

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
                                         channelNum=self.channelNum)
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

            p1 = pg.plot(title = "Ratio vs. Position")
            p1.addLegend()

            ratioX = np.linspace(1.,20.,num=1900)

            for region, ratioMap in enumerate(self.mapping):

                lineName = "  Region " + str(region)
                p1.plot(ratioMap,ratioX, pen=(region,len(self.mapping)),
                        name=lineName)

            p1.setLabel('left',"Ratio")
            p1.setLabel('bottom',"Position within region", units='mm')
            p1.showGrid(x=True,y=True)

            import sys
            if(sys.flags.interactive != 1) or not hasattr(QtCore,
                                                          'PYQT_VERSION'):
                QtGui.QApplication.instance().exec_()

        else:

            # Plots the current mapping between ratio and position for the
            # region listed

            print "Plotting map for regions ", regions, "...\n"

            p1 = pg.plot(title = "Ratio vs. Position")
            p1.addLegend()

            ratioX = np.linspace(1.,20.,num=1900)

            for i,region in enumerate(regions):
                lineName = "  Region " + str(region)
                p1.plot(self.mapping[region,:],ratioX,pen=(i,len(regions)),
                                                    name=lineName)

            p1.setLabel('left',"Ratio")
            p1.setLabel('bottom',"Position within region", units='mm')
            p1.showGrid(x=True,y=True)

            import sys
            if(sys.flags.interactive != 1) or not hasattr(QtCore,
                                                          'PYQT_VERSION'):
                QtGui.QApplication.instance().exec_()

    def plotHist(self, regions = None):

        '''Usage: plotHist(region = None)

        region(int): Region to be plotted. If None, plots all regions.

        Plots the current ratio histograms for the regions.

        *** Does not need event type update. *** '''

        if regions == None:

            # Plot all regions

            print "Plotting ratio histogram for all regions...\n"

            histPlot = pg.plot(title = "Ratio Histograms")
            histPlot.addLegend()

            histPlot.setLabel('left',"Counts")
            histPlot.setLabel('bottom',"Ratio")

            for i,hist in enumerate(self.rhist):

                histName = "  Region " + str(i)
                histPlot.plot(hist, pen=(i,len(self.rhist)), name=histName)

            import sys
            if(sys.flags.interactive != 1) or not hasattr(QtCore,
                                                          'PYQT_VERSION'):
                QtGui.QApplication.instance().exec_()

        else:

            # Plot the region listed

            print "Plotting ratio histogram for region", regions, "...\n"

            histPlot = pg.plot(title = "Ratio Histogram")
            histPlot.addLegend()

            histPlot.setLabel('left',"Counts")
            histPlot.setLabel('bottom',"Ratio")

            for i,region in enumerate(regions):

                histName = "  Region " + str(region)
                histPlot.plot(self.rhist[region,:],pen=(i,len(regions)),
                              name=histName)

            import sys
            if(sys.flags.interactive != 1) or not hasattr(QtCore,
                                                          'PYQT_VERSION'):
                QtGui.QApplication.instance().exec_()

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

            if e['isGood'] and max(e['pulseHeights'])>0 and \
                    max(e['pulseHeights'])<1000:

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

        self.WPm = ma.MaskedArray(self.WP,mask=self.WPmask)

        self.WPx = [num*self.stripPitch/2./len(self.WP[0]) 
            for num in range(len(self.WP[0]))]

        print "Done!"

    def plotWPs(self, masked=0):

        WPPlot = pg.plot(title = "Weighting Potentials")
        WPPlot.addLegend()

        WPPlot.setLabel('left',"Weighting Potential")
        WPPlot.setLabel('bottom',"Position (mm)")
        # Plotting the weighting potentials across space

        if masked == 0:
            for region,wp_r in enumerate(self.WP):
                WPname = " Region " + str(region)
                if region % 2 == 0:
                    WPPlot.plot(np.linspace(0,self.stripPitch/2.,
                            len(wp_r))+np.ones((len(wp_r)))*region*self.stripPitch/2.,wp_r,
                            pen=(region,len(self.WP)),name=WPname)
                else:
                    WPPlot.plot(np.linspace(0,self.stripPitch/2.,
                            len(wp_r))+np.ones((len(wp_r)))*region*self.stripPitch/2.,wp_r[::-1],
                            pen=(region,len(self.WP)),name=WPname)

        elif masked == 1:
            for region,wp_rm in enumerate(self.WPm):
                WPname = " Region " + str(region)
                if region % 2 == 0:
                    xm = ma.array(np.linspace(0,self.stripPitch/2.,
                        len(wp_rm))+np.ones((len(wp_rm)))*region*self.stripPitch/2.,
                        mask=ma.getmaskarray(wp_rm))
                    
                    WPPlot.plot(xm, wp_rm, pen=(region,len(self.WP)), name=WPname)

                else:
                    
                    xm = ma.array(np.linspace(0,self.stripPitch/2.,
                        len(wp_rm))+np.ones((len(wp_rm)))*region*self.stripPitch/2.,
                        mask=ma.getmaskarray(wp_rm))
                    
                    WPPlot.plot(xm, wp_rm[::-1], pen=(region,len(self.WP)), name=WPname)

        WPPlot.showGrid(x=True,y=True)
        
        import sys
        if(sys.flags.interactive != 1) or not hasattr(QtCore,
                                                      'PYQT_VERSION'):
            QtGui.QApplication.instance().exec_()

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

        print "Done!\n\n"

    def plotEnergyCal(self):

        ''' *** Does not need event type update. *** '''

        EhistPlot = pg.plot(title = "Calibration Data")

        EhistPlot.setLabel('left',"Counts")
        EhistPlot.setLabel('bottom',"Energy (keV)")

        Ecurve = pg.PlotCurveItem(self.EbinEdges,self.Ehist,stepMode=True)
        EhistPlot.addItem(Ecurve)

        import sys
        if(sys.flags.interactive != 1) or not hasattr(QtCore,
                                                          'PYQT_VERSION'):
            QtGui.QApplication.instance().exec_()

    def gatherPositions(self,regions=None,fnames=None):

        positions = []

        if regions is not None:

            for i,region in enumerate(regions):

                positions.append([])

                for event in self.allEvents:

                    if event['isGood'] and event['regionMain'] == region:

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

                filePath = 'data/' + fileName
                prsr = pp.pixieParser(fname=filePath,moduleNum=self.moduleNum,
                                      channelNum=self.channelNum)

                prsr.readBinFile()

                eventList = prsr.makeAndWriteEvents()
                
                for event in eventList:

                    check1 = np.floor(event['ratioMain']*100.) < self.numBins-1
                    check2 = event['ratioMain'] >= 1.

                    if check1 and check2 and event['isGood']:

                        event['x'] = self.mapEvent(e=event,xOnly=True)

                        if event['regionMain']%2 == 0:
                            positions[i].append(event['x'] + 
                                    (np.argmax(event['pulseHeights'])-1.)*self.stripPitch)
                        else:
                            positions[i].append(np.argmax(event['pulseHeights'])*self.stripPitch
                                    - event['x'])

        else:
            
            for event in self.allEvents:

                if event['isGood']:

                    if event['regionMain']%2 == 0:
                        positions.append(event['x'] + 
                                (np.argmax(event['pulseHeights'])-1.)*self.stripPitch)
                    else:
                        positions.append(np.argmax(event['pulseHeights'])*self.stripPitch
                                - event['x'])

        return positions

    def plotPositionHists(self,regions=None,fnames=None):

        posHistPlot = pg.plot(title = "Event Position Distribution")
        posHistPlot.setLabel('left',"Counts")
        posHistPlot.setLabel('bottom',"Position (mm)")

        if regions is not None:

            positions = self.gatherPositions(regions=regions)

            for i,region in enumerate(regions):

                histName = "Region " + str(region)

                hist,binEdges = np.histogram(positions[i],bins=1000,range=(0.,30.0))

                posCurve = pg.PlotCurveItem(binEdges,hist,stepMode=True,name=histName)

                posHistPlot.addItem(posCurve)

        elif fnames is not None:

            positions = self.gatherPositions(fnames=fnames)

            for i,fileName in enumerate(fnames):

                hist,binEdges = np.histogram(positions[i],bins=1000,range=(0.,30.0))

                posCurve = pg.PlotCurveItem(binEdges,hist,stepMode=True,name=fileName)

                posHistPlot.addItem(posCurve)

        else:

            positions = self.gatherPositions()

            hist,binEdges = np.histogram(positions,bins=1000,range=(0.,30.0))

            posCurve = pg.PlotCurveItem(binEdges,hist,stepMode=True,name="All Events")

            posHistPlot.addItem(posCurve)

        import sys
        if(sys.flags.interactive != 1) or not hasattr(QtCore,'PYQT_VERSION'):
            QtGui.QApplication.instance().exec_()

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
