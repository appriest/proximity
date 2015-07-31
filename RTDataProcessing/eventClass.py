import numpy as np

class event:

    def __init__(self, pulseHeights, t=None, minHeight = 50):

        self.pulseHeights = [float(pulseHeight) for\
                             pulseHeight in  pulseHeights]
        self.t = t

        # numStrips is the number of strips per side of the detector
        # (includes 0) maxStrip is the index of the largest signal, with
        # indices starting at 0
        self.numStrips = len(pulseHeights)
        self.maxStrip = np.argmax(pulseHeights)

        # Sets the minimum pulse height to be considered a good event
        self.minHeight = minHeight

        if self.maxStrip == 0 or self.maxStrip == self.numStrips-1:

            # The event occurred under an edge strip, and is not a good event
            self.regionMain = -1
            self.ratioMain = -1

        elif self.pulseHeights[self.maxStrip] < self.minHeight \
            or self.pulseHeights[self.maxStrip-1] < self.minHeight \
            or self.pulseHeights[self.maxStrip+1] < self.minHeight:

            # The event doesn't meet the minimum pulse height requirements,
            # and is not a good event
            self.regionMain = -2
            self.ratioMain = -2

        else:

            #The event has passed all requirements and is a good event

            # The event is to the right of the max strip
            if self.maxStrip + 1 > self.maxStrip - 1:

                # Main event info used to reconstruct the event
                self.regionMain = 2*self.maxStrip - 1
                self.ratioMain = self.pulseHeights[self.maxStrip]/ \
                    self.pulseHeights[self.maxStrip+1]

                # Secondary region for meta reconstruction purposes
                self.regionSec = 2*self.maxStrip - 2
                self.ratioSec = self.pulseHeights[self.maxStrip]/ \
                    self.pulseHeights[self.maxStrip-1]

            # The event is to the left of the max strip
            elif self.maxStrip + 1 < self.maxStrip - 1:

                # Main event info used to reconstruct the event
                self.regionMain = 2*self.maxStrip - 2
                self.ratioMain = self.pulseHeights[self.maxStrip]/ \
                    self.pulseHeights[self.maxStrip-1]

                # Secondary region for meta reconstruction purposes
                self.regionSec = 2*self.maxStrip - 1
                self.ratioSec = self.pulseHeights[self.maxStrip]/ \
                    self.pulseHeights[self.maxStrip+1]

    def isGoodEvent(self):

        if self.regionMain > 0:

            return 1

        else:

            return 0

    def returnRatioMain(self):

        return self.ratioMain

    def returnRatioSec(self):

        return self.ratioSec

    def returnRegionMain(self):

        return self.regionMain

    def returnRegionSec(self):

        return self.regionSec
