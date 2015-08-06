import numpy as np
import scipy as sp
from eventClass import event
import matplotlib.pyplot as plt
import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtCore
#import matplotlib.pyplot as plt

class calibration:

    def __init__(self, calType = 0, stripPitch = 5., numBins = 2000, \
                 moduleNum=2, channelNum=[4,4]):

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

    def addEvent(self, e = None):

        ''' Usage: addEvent(e = eventClass.event)

        Adds the event ratio to the proper histogram and adds one to the
        number of events for the region.'''

        # rhist is an array containing the ratio histograms(regions = rows)
        # for each of the regions (bins = columns)

        if isinstance(e,event) == False:
            print "You didn't provide an event to add! Try again...\n"
            return 1

        if e.ratioMain*100 < self.numBins and e.regionMain >= 0:
            self.rhist[e.regionMain, np.floor(100*e.ratioMain)] += 1
            self.numEvents[e.regionMain] += 1

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

        import pixieBinParser2 as pp

        if fname is not None:

            print "Reading ", fname, "..."
            prsr = pp.pixieParser(fname=fname,moduleNum=self.moduleNum,
                                  channelNum=self.channelNum)

            prsr.readBinFile()

            eventList = prsr.makeAndWriteEvents()

            for e in eventList:

                self.addEvent(e)

            print "Done!\n"

        elif folderName is not None:

            import os

            curDir = os.getcwd()

            fileDir = curDir + '/' + folderName

            eventList = []

            for thisFile in os.listdir(fileDir):

                if thisFile[-4:] == '.bin':

                    print "Reading ", thisFile, "..."
                    prsrPath = folderName + '/' + thisFile
                    prsr = pp.pixieParser(fname=prsrPath,
                                         moduleNum=self.moduleNum,
                                         channelNum=self.channelNum)
                    prsr.readBinFile()
                    eventList = prsr.makeAndWriteEvents()

                    for e in eventList:
                        self.addEvent(e)

                    del prsr
                    print "Done!\n"

                else:

                    print "Skipping ", thisFile, ", because it is not a \
                        .bin file..."

            print "Done!\n"

        else:

            print "You didn't specify anything!\n"
            return 1

        self.updateMap()

    def updateMap(self):

        '''Usage: updateMap()

        Integrates over the ratio histograms for each region creating the
        mapping from ratio to position.'''

        # Updates the mapping from ratio to position
        # Performs an integral on the histograms for each of the regions

        print "Updating map plot...\n"

        self.mapping = np.array([[sum(subArray[0:i+100])/self.numEvents[j] \
                                  for i,ratio in enumerate(subArray[100:])] \
                                 for j,subArray in enumerate(self.rhist)])

        self.mapping = self.mapping*self.stripPitch/2.

        self.plotMap()

    def plotMap(self, regions = None):

        '''Usage: plotMap(region = None)

        region(int): If region is provided, only the mapping for the region
            provided will be mapped. Otherwise, all regions will be plotted.

        Simply plots the mapping for the region given or for all regions.'''

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

        Plots the current ratio histograms for the regions.'''

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

    def writeCalToFile(self, fname = None):

        '''Usage: writeCalToFile(fname = None)

        fname("str"): String literal for the name of the calibration file.

        Implementation has not been written yet. More details to come.'''

        if fname == None:

            print "Please provide a file name!"

        else:
            # Write the current calibration to a file for later use

            print "Writing calibration to file: ", fname, "\n"

            # Write calibration

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

    def mapEvent(self, e = None):

        '''Usage: mapEvent(e = None)

        e(event object): Event instance to be mapped. The event position will
            be added to the attributes of the event instance.

        Take in an event and use the current mapping to reconstruct the
        position of the event

        For the love of god, take the print statements out before trying
        to use this for realsies'''

        if e == None:

            print "Don't forget to take these print statements out before \
                trying to use this!\n"
            print "Please provide a valid event of class type 'event'!\n"

        else:

            print "Don't forget to take these print statements out before \
                trying to use this!\n"
            print "Mapping event...\n"

            # Map event

            print "Done!\n\n"

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
