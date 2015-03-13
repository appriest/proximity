import struct
import eventClass.event as event
import numpy as np

class pixieParser:

    def __init__(self, fname=None):

        self.fname = fname

        if self.fname == None:

            print "Please enter a valid file name to properly initialize this class."

            return 0

        try:

            self.f = open(fname, 'rb')

        except IOError:

            print "The file you entered does not exist."

        print "Enter the number of modules used for this data: "

        self.moduleNum = raw_input()

        self.channelNum = np.zeros(self.moduleNum)

        for i in range(self.moduleNum):

            print "Enter the number of channels used in module ", i, ": "

            self.channelNum[i] = raw_input()

    def readRawFile(self):

        numBuffers = 0

        while True:

            buffersize, = struct.unpack('h', self.f.read(2))
            module, = struct.unpack('h', self.f.read(2))
            word, = struct.unpack('h', self.f.read(2))
            bufTimeHi, = struct.unpack('h', self.f.read(2))
            bufTimeMi, = struct.unpack('h', self.f.read(2))
            bufTimeLo, = struct.unpack('h', self.f.read(2))

            bufferTime = bufTimeHi*2**32 + bufTimeMi*2**16 + bufTimeLo
            numEvents = (buffersize - 6)/11
            numBuffers = numBuffers + 1

            for i in range(numEvents):

                if module == 0:

                    word, = struct.unpack('h', self.f.read(2))
                    eventTimeHi, = struct.unpack('h', self.f.read(2))
                    eventTimeLo, = struct.unpack('h', self.f.read(2))

                    for channel in range(self.channelNum[module]):

                        timeCh0, = struct.unpack('h', self.f.read(2))
                        energyCh0, = struct.unpack('h', self.f.read(2))
                        timeCh1, = struct.unpack('h', self.f.read(2))
                        energyCh1, = struct.unpack('h', self.f.read(2))
                        timeCh2, = struct.unpack('h', self.f.read(2))
                        energyCh2, = struct.unpack('h', self.f.read(2))
                        timeCh3, = struct.unpack('h', self.f.read(2))
                        enerfyCh3, = struct.unpack('h', self.f.read(2))

                        eventTime = bufTimeHi*2**32 + eventTimeHi*2**16 \
                            + eventTimeLo
