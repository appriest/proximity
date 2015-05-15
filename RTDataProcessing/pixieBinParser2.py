import struct
from eventClass import *
import numpy as np
import os

class pixieParser:

    def __init__(self, fname=None, quiet=1):

        self.fname = fname

        if self.fname is None:

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
            print fname, ": ", self.numbytes, " bytes"

        self.f.seek(0, os.SEEK_SET)

    def readBinFile(self):


        numBuffers = 0
        maxBuffers = 1000

        eventTimes = []
        self.energies = []

        for i in range(self.moduleNum):

            self.energies.append([])

            for j in range(int(self.channelNum[i])):

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

            print "Reading ", numEvents, " events from Module ", module, "..."

            for event in range(int(numEvents)):

                word, = struct.unpack('h', self.f.read(2))
                eventTimeHi, = struct.unpack('h', self.f.read(2))
                eventTimeLo, = struct.unpack('h', self.f.read(2))

                for channel in range(int(self.channelNum[module])):

                    timeCh, = struct.unpack('h', self.f.read(2))
                    energyCh, = struct.unpack('h', self.f.read(2))

                    self.energies[module][channel].append(energyCh)

                # Module number check prevents redundancy
                if module == 0:
                    eventTimes.append(bufTimeHi*2**32 + eventTimeHi*2**16 \
                        + eventTimeLo)

        self.e_objects = []
        chani = 0

        for mod in self.energies:

            for chan in mod:

                print "There are ", len(chan), " events in Ch. ", chani

                chani += 1

            #self.e_objects.append(event([e0,e1,e2,e3,e4,e5,e6,e7],t))
