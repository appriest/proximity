import numpy as np
import scipy as sp
from eventClass import event
import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtCore

class calibration:

    def __init__(self, calType = 0, stripPitch = 5, numBins = 2000, \
                 numStrips = 8):

        self.notes = ""
        self.calType = calType
        self.numStrips = numStrips
        self.numBins = numBins
        self.stripPitch = stripPitch
        self.numEvents = np.zeros(self.numStrips)
        self.rhist = np.zeros((self.numStrips,self.numBins))
        self.mapping = np.zeros((self.numStrips, self.numBins))

    def addEvent(self, e = event()):

        # rhist is an array containing the ratio histograms(regions = rows)
        # for each of the regions (bins = columns)
        self.rhist[np.floor(1000*e.ratio), e.region] += 1
        self.numEvents[e.region] += 1

    def updateMap(self):

        # Updates the mapping from ratio to position
        # Performs an integral on the histograms for each of the regions

        print "Updating map plot...\n"

        self.mapping = np.array([[sum(subArray[:i+1])/self.numEvents[j] \
                                 for i,ratio in enumerate(subArray)] \
                                 for j,subArray in enumerate(self.rhist)])

        self.mapping = self.mapping*self.stripPitch

    def plotMap(self, region = None):

        if region == None:

            # Plots the current mapping between ratio and position for all
            # regions

            print "Plotting map for all regions...\n"

            win = pg.GraphicsWindow(title="Ratio to Position Mapping")
            p1 = win.addPlot(title = "Ratio vs. Position")

            x = np.arange(self.numBins)/self.numBins*self.stripPitch

            for region, ratioMap in enumerate(self.mapping):

                p1.plot(x,ratioMap)

        else:

            # Plots the current mapping between ratio and position for the
            # region listed

            print "Plotting map for region ", region, "...\n"

    def plotHist(self, region = None):

        # Plots the current histograms for the regions

        if region == None:

            # Plot all regions

            print "Plotting ratio histogram for all regions...\n"

        else:

            # Plot the region listed

            print "Plotting ratio histogram for region ", region, "...\n"

    def writeCalToFile(self, fname = None):

        if fname == None:

            print "Please provide a file name!"

        else:
            # Write the current calibration to a file for later use

            print "Writing calibration to file: ", fname, "\n"

            # Write calibration

            print "...\nFinished!"

    def readCalFromFile(self, fname = None):

        # Read a saved calibration from a file

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

        # Take in an event and use the current mapping to reconstruct the
        # position of the event

        '''For the love of god, take the print statements out before trying
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

        print "This calibration object is for a(n) ", self.numStrips, \
            " strip detector.\n"
        print "Strip pitch: ", self.stripPitch, "\n"
        print "Number of events: ", self.numEvents, "\n"
        print "Notes: ", self.notes, "\n\n"

    def addNotes(self, note = None):

        # Function for adding notes to a calibration that give some
        # information about the object

        self.notes += " "
        self.notes += note
