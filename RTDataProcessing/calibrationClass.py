import numpy as np
import scipy as sp
from eventClass import event
import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtCore
import matplotlib.pyplot as plt

class calibration:

    def __init__(self, calType = 0, stripPitch = 5., numBins = 2000, \
                 numStrips = 8):

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
        self.numStrips = numStrips
        self.numBins = numBins
        self.stripPitch = stripPitch
        self.numEvents = np.zeros(self.numStrips)
        self.rhist = np.zeros((self.numStrips,self.numBins))
        self.mapping = np.zeros((self.numStrips, self.numBins))

    def addEvent(self, e = None):

        ''' Usage: addEvent(e = eventClass.event)

        Adds the event ratio to the proper histogram and adds one to the
        number of events for the region.'''

        # rhist is an array containing the ratio histograms(regions = rows)
        # for each of the regions (bins = columns)

        if isinstance(e,event) == False:
            print "You didn't provide an event to add! Try again...\n"
            return 1

        self.rhist[e.regionMain, np.floor(1000*e.ratioMain)] += 1
        self.numEvents[e.regionMain] += 1

    def updateMap(self):

        '''Usage: updateMap()

        Integrates over the ratio histograms for each region creating the
        mapping from ratio to position.'''

        # Updates the mapping from ratio to position
        # Performs an integral on the histograms for each of the regions

        print "Updating map plot...\n"

        self.mapping = np.array([[sum(subArray[:i+1])/self.numEvents[j] \
                                 for i,ratio in enumerate(subArray)] \
                                 for j,subArray in enumerate(self.rhist)])

        self.mapping = self.mapping*self.stripPitch/2.

        self.plotMap()

    def plotMap(self, region = None):

        '''Usage: plotMap(region = None)

        region(int): If region is provided, only the mapping for the region
            provided will be mapped. Otherwise, all regions will be plotted.

        Simply plots the mapping for the region given or for all regions.'''

        if region == None:

            # Plots the current mapping between ratio and position for all
            # regions

            print "Plotting map for all regions...\n"

            win = pg.GraphicsWindow(title="Ratio to Position Mapping")
            p1 = win.addPlot(title = "Ratio vs. Position")

            x = np.arange(self.numBins)/self.numBins*self.stripPitch

            for region, ratioMap in enumerate(self.mapping):

                p1.plot(x,ratioMap)

            p1.setLabel('left',"Ratio")
            p1.setLabel('bottom',"Position within region", units='mm')

            import sys
            if(sys.flags.interactive != 1) or not hasattr(QtCore,
                                                          'PYQT_VERSION'):
                QtGui.QApplication.instance().exec_()

        else:

            # Plots the current mapping between ratio and position for the
            # region listed

            print "Plotting map for region ", region, "...\n"

            win = pg.GraphicsWindow(title="Ratio to Position Mapping")
            p1 = win.addPlot(title = "Ratio vs. Position")

            x = np.arange(self.numBins)/self.numBins*self.stripPitch

            p1.plot(x,self.mapping[:,region])

            p1.setLabel('left',"Ratio")
            p1.setLabel('bottom',"Position within region", units='mm')

            import sys
            if(sys.flags.interactive != 1) or not hasattr(QtCore,
                                                          'PYQT_VERSION'):
                QtGui.QApplication.instance().exec_()

    def plotHist(self, region = None):

        '''Usage: plotHist(region = None)

        region(int): Region to be plotted. If None, plots all regions.

        Plots the current ratio histograms for the regions.'''

        if region == None:

            # Plot all regions

            print "Plotting ratio histogram for all regions...\n"

            histWin = pg.GraphicsWindow(title="Ratio Histograms for All \
                                        Regions")

            histPlot = histWin.addPlot(title = "Ratio Histograms")

            histPlot.setLabel('left',"Counts")
            histPlot.setLabel('bottom',"Ratio")

            for hist in self.rhist:

                histPlot.plot(hist)

            import sys
            if(sys.flags.interactive != 1) or not hasattr(QtCore,
                                                          'PYQT_VERSION'):
                QtGui.QApplication.instance().exec_()

        else:

            # Plot the region listed

            print "Plotting ratio histogram for region", region, "...\n"

            title = "Ratio Histogram for Region " + str(region)
            histWin = pg.GraphicsWindow(title=title)

            histPlot = histWin.addPlot(title = "Ratio Histogram")

            histPlot.setLabel('left',"Counts")
            histPlot.setLabel('bottom',"Ratio")

            histPlot.plot(self.rhist[region,:])

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
