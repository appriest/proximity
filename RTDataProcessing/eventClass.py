import numpy as np

class event:

    def __init__(self, pulseHeights, t=None, minHeight = 50):

        self.pulseHeights = [float(pulseHeight) for pulseHeight in  pulseHeights]
        self.t = t
        
        # numStrips is the number of strips per side of the detector (includes 0)
        # maxStrip is the index of the largest signal, with indices starting at 0
        self.numStrips = len(pulseHeights)
        self.maxStrip = np.argmax(pulseHeights)
        
        # Sets the minimum pulse height to be considered a good event
        self.minHeight = minHeight

        if self.maxStrip == 0 or self.maxStrip == self.numStrips-1:

            # The event occurred under an edge strip, and is not a good event
            self.regionMain = -1
            self.ratioMain = -1

        elif self.pulseHeights[self.maxStrip] < self.minHeight:

            # The event doesn't meet the minimum pulse height requirements, and is not a good event
            self.regionMain = -2
            self.ratioMain = -2

        else:

            #The event has passed all requirements and is a good event
            if self.maxStrip + 1 > self.maxStrip - 1:

                # Main event info used to reconstruct the event
                self.regionMain = 2*self.maxStrip - 1
                self.ratioMain = self.pulseHeights[self.maxStrip]/self.pulseHeights[self.maxStrip+1]
                
                # Secondary region for meta reconstruction purposes
                self.regionSec = 2*self.maxStrip - 2
                self.ratioSec = self.pulseHeights[self.maxStrip]/self.pulseHeights[self.maxStrip-1]

            elif self.maxStrip + 1 < self.maxStrip - 1:

                self.regionMain = 2*self.maxStrip - 2
                self.ratioMain = self.pulseHeights[self.maxStrip]/self.pulseHeights[self.maxStrip-1]

                self.regionSec = 2*self.maxStrip - 1
                self.ratioSec = self.pulseHeights[self.maxStrip]/self.pulseHeights[self.maxStrip+1]

    def isGoodEvent(self):

        if self.regionMain > 0:

            return 1

        else:

            return 0


