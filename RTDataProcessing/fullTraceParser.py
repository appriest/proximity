import struct
import numpy as np
import os
import time

def readFile(fname=None,moduleNum=2,channelNum=[4,4],dataLim=10000):

    try:
        f = open(fname, 'rb')

    except IOError:

        print "There was a problem opening this file..."
        return None

    f.seek(0, os.SEEK_END)
    numBytes = f.tell()

    print fname, ": ", numBytes, " bytes"

    f.seek(0, os.SEEK_SET)

    numBuffers = 0
    maxBuffers = 10000

    eventTimes = []
    energies = []

    traces = []

    data = []

    dataPos = 0

    for i in range(moduleNum):

        energies.append([])
        traces.append([])

        for j in range(int(channelNum[i])):

            energies[i].append([])
            traces[i].append([])

    while True:

        if f.tell() >= numBytes - 1:
            break
        elif dataPos > dataLim:
            break

        dataPos += 1

        datapoint, = struct.unpack('h', f.read(2))
        data.append(datapoint)

        '''
        buffersize, = struct.unpack('h', f.read(2))
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

            for channel in range(int(self.channelNum[module])):

                timeCh, = struct.unpack('h', self.f.read(2))
                energyCh, = struct.unpack('h', self.f.read(2))

                self.energies[module][channel].append(energyCh)

            # Module number check prevents redundancy
            eTime = bufTimeHi*2**32 + eventTimeHi*2**16 + eventTimeLo
            self.eventTimes.append(eTime)
        '''

    return data
