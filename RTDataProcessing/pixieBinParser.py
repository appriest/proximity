import struct
from eventClass import *
import numpy as np
import os
import time
import numpy.ma as ma

class pixieParser:

    '''
    File: pixieBinParser2.py
    Author: Anders Priest
    Description: Pixie parser is meant for binary files written by the Pixie
        Igor software. It currently has the ability to write text files.
        Future capabilities include being able to populate event objects
        for use with the rest of the Proximity analysis software.

    __init__(self, fname=None, quiet=1, moduleNum=None, channelNum=None):

        fname: .bin file written by the Pixie Igor software
        quiet: supresses printed output
        moduleNum: number of modules used for acquisition
        channelNum: number of channels used for each module; list must have
            the same dimension as moduleNum (i.e. 1xmoduleNum)
    '''

    def __init__(self, fname=None, quiet=1, moduleNum=None, channelNum=None, 
            minHeight = 0., channelConfig = None):

        self.fname = fname
        self.goodEvents = 0
        self.minHeight = minHeight
        self.channelConfig = channelConfig

        if self.fname[-3:] == 'txt':
            self.txt=True
        else:
            self.txt=False

        if self.fname is None:

            print "Please enter a valid file name to properly initialize this \
                class."

            return 1

        try:

            if self.txt:
                self.f = open(fname)
            else:
                self.f = open(fname, 'rb')

        except IOError:

            print "The file you entered does not exist."
            return None

        if moduleNum is None:

            print "Enter the number of modules used for this data: "

            self.moduleNum = int(raw_input())

            self.channelNum = np.zeros(self.moduleNum)

            for i in range(int(self.moduleNum)):

                print "Enter the number of channels used in module ", i, ": "

                self.channelNum[i] = raw_input()

        else:

            self.moduleNum = moduleNum
            self.channelNum = channelNum

        if self.moduleNum != len(self.channelNum):

            print "The length of the list 'channelNum' must equal the number "
            print "of modules, 'moduleNum', given."

            return 1

        self.f.seek(0, os.SEEK_END)
        self.numbytes = self.f.tell()

        if quiet == 0:
            print fname, ": ", self.numbytes, " bytes"

        self.f.seek(0, os.SEEK_SET)

    def readTextFile(self,quiet=1):

        self.f.seek(0, os.SEEK_END)
        numbytes = self.f.tell()

        self.f.seek(0)
        
        self.f.readline()
        self.f.readline()

        events = []

        while self.f.tell() < numbytes:

            event = []
            for i in range(8):

                event.append(float(self.f.read(8)))
                self.f.read(1)

            events.append(event)

        self.txtArray = events
        self.eventTimes = list(np.zeros(len(events)))

    def readBinFile(self,quiet=1):

        '''
        File: pixieBinParser2.py
        Author: Anders Priest
        Description: Once initialized, execute this function to read the file.
                This will populate self.energies and self.eventTimes as read
                    eventArray['isGood'][num] = True
                from the binary file.
        '''

        numBuffers = 0
        maxBuffers = 1000

        self.eventTimes = []
        self.energies = []

        for i in range(self.moduleNum):

            self.energies.append([])

            for j in range(int(4)):   # replace 4 with self.channelNum[i if 4 doesn't work]

                self.energies[i].append([])

        while True:

            if self.f.tell() >= self.numbytes-10:
                break

            buffersize, = struct.unpack('h', self.f.read(2))
            module, = struct.unpack('h', self.f.read(2))
            word, = struct.unpack('h', self.f.read(2))
            bufTimeHi, = struct.unpack('h', self.f.read(2))
            bufTimeMi, = struct.unpack('h', self.f.read(2))
            bufTimeLo, = struct.unpack('h', self.f.read(2))


            bufferTime = bufTimeHi*2**32 + bufTimeMi*2**16 + bufTimeLo
            numEvents = (buffersize - 6)/11
            numBuffers = numBuffers + 1

            if quiet != 1:
                print "Reading ", numEvents, " events from Module ", module, \
                    "..."

            for event in range(int(numEvents)):

                word, = struct.unpack('h', self.f.read(2))
                eventTimeHi, = struct.unpack('h', self.f.read(2))
                eventTimeLo, = struct.unpack('h', self.f.read(2))

                # Put this back in if 4 channel read does not work
                # for channel in range(int(self.channelNum[module])):   
                for channel in range(4):

                    timeCh, = struct.unpack('h', self.f.read(2))
                    energyCh, = struct.unpack('h', self.f.read(2))

                    #if channel<self.channelNum[module]: # Take this out if 4 channel read does not work
                    self.energies[module][channel].append(energyCh)

                # Module number check prevents redundancy
                eTime = bufTimeHi*2**32 + eventTimeHi*2**16 + eventTimeLo
                self.eventTimes.append(eTime)
                '''
                if len(self.eventTimes) == 0:
                    self.eventTimes.append(eTime)
                elif eTime - self.eventTimes[-1] > 3:
                    self.eventTimes.append(eTime)
                # else:
                    # Do nothing; these would be redundant events
                '''

        chani = 0

        if quiet != 1:
            for mod in self.energies:

                for chan in mod:

                    print "There are ", len(chan), " events in Ch. ", chani

                    chani += 1
        '''
        print "len(eventTimes): ", len(self.eventTimes)
        print "len(energies[0][0]: ", len(self.energies[0][0])
        print "len(energies[1][0]: ", len(self.energies[1][0])
        print "Example event: ", self.energies[0][0][0], ',', \
            self.energies[0][1][0], ',',\
            self.energies[0][2][0], ',',\
            self.energies[0][3][0], ',',\
            self.energies[1][0][0], ',',\
            self.energies[1][1][0], ',',\
            self.energies[1][2][0], ',',\
            self.energies[1][3][0]
        '''

    def writeTxtFile(self):

        '''
        File: pixieBinParser2.py
        Author: Anders Priest
        Description: This function will write a text file containing the data
            from the binary file, with the same base name. The data is
            formatted for easy reading.
        '''

        fname = self.fname
        fname = list(fname)
        fname[-3:] = ['t','x','t']
        fname = "".join(fname)
        if os.path.isfile(fname):
            print "This text version of this file already exists."
            print "Would you like to overwrite it? (y/n)"
            overwrite = raw_input()
            if str.lower(overwrite) == 'y':
                f = open(fname,'w')
            else:
                print "File not overwritten. Exiting,,,"
                return 0
        else:
            f = open(fname,'w')

        f.write("# This file was written from pixieBinParser2.py and was\n")
        f.write("# parsed from ")
        f.write(self.fname)
        f.write(". The file has been reformatted.\n")
        f.write("# It was written on ")
        f.write(time.strftime("%b %d, %Y"))
        f.write("\n")
        f.write("\n\n# pixieBinParser2.py was written by Anders Priest.")
        f.write("\n\n\n")

        totalCh = 0
        for chNum in self.channelNum:

            totalCh += chNum

        dim0 = max([len(self.energies[0][0]),len(self.energies[1][0])])
        outputArray = np.zeros((dim0,totalCh))

        for m,module in enumerate(self.energies):

            for ch,channel in enumerate(module):

                for i,eventEnergy in enumerate(channel):

                    outputArray[i,ch+4*m] = eventEnergy

        outputArray = list(outputArray)

        f.write("Time\t\t")
        for i in range(int(totalCh)):

            f.write("E"+str(i))
            f.write("\t")

        f.write("\n\n")

        for num,event in enumerate(outputArray):

            f.write(str(self.eventTimes[num]))
            f.write("\t")

            for chan in event:

                f.write(str(chan))
                f.write("\t")

            f.write("\n")

        f.write("\n\n")
        f.write("End of File")

        print "Finished writing file."
        print len(outputArray), "events written."

    def makeAndWriteEvents(self, returnArray=1):

        '''
        File: pixieBinParser2.py
        Author: Anders Priest
        Description: This function SHOULD populate event objects then either
            return them or write them to a file. At the time of writing this
            none of the functionality has been written.
        '''
        if self.txt != True:
            totalCh = 0

            for chNum in self.channelNum:

                totalCh += chNum

            dim0 = max([len(self.energies[0][0]),len(self.energies[1][0])])
            outputArray = np.zeros((dim0,totalCh))

            for m,module in enumerate(self.energies):

                if self.channelConfig is not None:
                    if m == 0:
                        index = 0
                    else:
                        index = m*len(self.channelConfig[m-1])

                for ch,channel in enumerate(module):

                    if self.channelConfig is None:

                        for i,eventEnergy in enumerate(channel):

                            outputArray[i,ch+4*m] = eventEnergy

                    elif ch in self.channelConfig[m]:

                        for i,eventEnergy in enumerate(channel):

                            outputArray[i,index] = eventEnergy

                        index += 1

                    else:

                        continue

            outputArray = list(outputArray)

        else:

            outputArray = self.txtArray

        dt = np.dtype([('pulseHeights',np.int32,(len(outputArray[0]),)),
                ('regionMain',np.int8),
                ('regionSec',np.int8),
                ('ratioMain',np.float64),
                ('ratioSec',np.float64),
                ('t',np.uint32),
                ('x',np.float32),
                ('E',np.float64),
                ('isGood',np.bool_)])

        eventArray = np.zeros((len(self.eventTimes,)),dtype=dt)

        for num,pulseHeight in enumerate(outputArray):

            eventArray['pulseHeights'][num] = pulseHeight
            eventArray['t'][num] = self.eventTimes[num]

            # Note: These checks will not work on multi-site events. Change to check all
            #   channels for second highest pulse height

            if np.argmax(pulseHeight) != 0 and np.argmax(pulseHeight) != sum(self.channelNum)-1 \
                and max(pulseHeight)>self.minHeight:

                regionLeftCheck = np.sum(pulseHeight[np.argmax(pulseHeight)-1]* \
                        np.ones(len(pulseHeight)) > pulseHeight)

                regionRightCheck = np.sum(pulseHeight[np.argmax(pulseHeight)+1]* \
                        np.ones(len(pulseHeight)) > pulseHeight)

                numCheck = sum(self.channelNum)-2

                if regionLeftCheck == numCheck and pulseHeight[np.argmax(pulseHeight)-1] != 0:
            
                    if pulseHeight[np.argmax(pulseHeight)-1] > self.minHeight:
                        eventArray['regionMain'][num] = 2 * np.argmax(pulseHeight) - 2
                        eventArray['regionSec'][num] = 2 * np.argmax(pulseHeight) - 1
                        eventArray['ratioMain'][num] = pulseHeight[np.argmax(pulseHeight)]/ \
                                        pulseHeight[np.argmax(pulseHeight)-1]
                        eventArray['ratioSec'][num] = pulseHeight[np.argmax(pulseHeight)]/ \
                                        pulseHeight[np.argmax(pulseHeight)+1]
                        eventArray['isGood'][num] = True
                        self.goodEvents += 1
                    else:
                        eventArray['regionMain'][num] = -1
                        eventArray['regionSec'][num] = -1
                        eventArray['ratioMain'][num] = -1
                        eventArray['ratioSec'][num] = -1
                        eventArray['isGood'][num] = False

                elif regionRightCheck == numCheck and pulseHeight[np.argmax(pulseHeight)+1] != 0:

                    if pulseHeight[np.argmax(pulseHeight)+1] > self.minHeight:
                        eventArray['regionMain'][num] = 2 * np.argmax(pulseHeight) - 1
                        eventArray['regionSec'][num] = 2 * np.argmax(pulseHeight) - 2
                        eventArray['ratioMain'][num] = pulseHeight[np.argmax(pulseHeight)]/ \
                                        pulseHeight[np.argmax(pulseHeight)+1]
                        eventArray['ratioSec'][num] = pulseHeight[np.argmax(pulseHeight)]/ \
                                        pulseHeight[np.argmax(pulseHeight)-1]
                        eventArray['isGood'][num] = True
                        self.goodEvents += 1
                    else:
                        eventArray['regionMain'][num] = -1
                        eventArray['regionSec'][num] = -1
                        eventArray['ratioMain'][num] = -1
                        eventArray['ratioSec'][num] = -1
                        eventArray['isGood'][num] = False

                else:

                    eventArray['regionMain'][num] = -1
                    eventArray['regionSec'][num] = -1
                    eventArray['ratioMain'][num] = -1
                    eventArray['ratioSec'][num] = -1
                    eventArray['isGood'][num] = False

            else:

                eventArray['regionMain'][num] = -1
                eventArray['regionSec'][num] = -1
                eventArray['ratioMain'][num] = -1
                eventArray['ratioSec'][num] = -1
                eventArray['isGood'][num] = False

        if returnArray:

            return eventArray

        else:

            import pickle

            fname = self.fname
            fname = list(fname)
            fname[-3:] = ['p','k','l']
            fname = "".join(fname)
            outFile = open(fname, 'w')
            pickle.dump(eventObjs,outFile)
