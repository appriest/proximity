import struct
import eventClass as ec
import numpy as np
import os

class pixieParser:

    def __init__(self, fname=None, quiet=1):

        self.fname = fname

        if self.fname == None:

            print "Please enter a valid file name to properly initialize this \
                class."

            return 0

        try:

            self.f = open(fname, 'rb')

        except IOError:

            print "The file you entered does not exist."

        print "Enter the number of modules used for this data: "

        self.moduleNum = int(raw_input())

        self.channelNum = np.zeros(self.moduleNum)

        for i in range(int(self.moduleNum)):

            print "Enter the number of channels used in module ", i, ": "

            self.channelNum[i] = raw_input()

        self.f.seek(0, os.SEEK_END)
        self.numbytes = self.f.tell()

        if quiet == 0:
            print fname, ": ", numbytes, " bytes"

        self.f.seek(0, os.SEEK_SET)

    def readBinFile(self):


        numbuffers = 0
        maxBuffers = 1000

        while numBytesRead < self.numbytes:

            if self.f.tell() >= self.numbytes:
                return 0

            buffersize, = struct.unpack('h', self.f.read(2))
            module, = struct.unpack('h', self.f.read(2))
            word, = struct.unpack('h', self.f.read(2))
            bufTimeHi, = struct.unpack('h', self.f.read(2))
            bufTimeMi, = struct.unpack('h', self.f.read(2))
            bufTimeLo, = struct.unpack('h', self.f.read(2))

            bufferTime = bufTimeHi*2**32 + bufTimeMi*2**16 + bufTimeLo
            numEvents = (buffersize - 6)/11
            numBuffers = numBuffers + 1


