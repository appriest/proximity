import numpy as np
import scipy as sp
from eventClass import event

class calibration:

    def __init__(self, calType = 0, stripPitch = 5, numBins = 2000, numStrips = 8):

        self.calType = calType
        self.numStrips = numStrips
        self.numBins = numBins
        self.stripPitch = stripPitch
        self.numEvents = 0
        self.rhist = np.zeros((self.numStrips,self.numBins))
    
    def addEvent(self, event):
        
        # rhist is an array containing the ratio histograms(regions = rows) for each of the regions (bins = columns)
        self.rhist[event.region][np.floor(1000*event.ratio)] += 1
        self.numEvents += 1

    def updateMap(self):

        # Updates the mapping from ratio to position
        # Performs an integral on the histograms for each of the regions

    def plotMap(self):

        # Plots the current mapping between ratio and position

    def plotHist(self, region = None):

        # Plots the current histograms for the regions

        if region == None:

            # Plot all regions

        else:

            # Plot the region listed

    def writeCalToFile(self, fname):

        # Write the current calibration to a file for later use

    def readCalFromFile(self, fname):

        # Read a saved calibration from a file

    def mapEvent(self, event):

        # Take in an event and use the current mapping to reconstruct the position of the event
