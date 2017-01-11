import numpy as np
import scipy as sp
from eventClass import event
import matplotlib.pyplot as plt
import matplotlib as mpl

# Change matplotlibs default font to courier for this script
mpl.rcParams['font.family']='cmr10'

colors = ['black', 'blue', 'green', 'red', 'cyan', 'magenta', 'yellow', 
            'burlywood', 'chartreuse', 'gray', 'darkorange', 'olive', 'sienna']

class calibration:

    def __init__(self, calType = 0, stripPitch = 5., numBins = 2000, \
                 moduleNum=2, channelNum=[4,4], numWPbins = 500,
                 maxWP = 0.75, minHeight=15.):

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
        self.moduleNum = moduleNum
        self.channelNum = channelNum
        self.numStrips = sum(self.channelNum)
        self.numBins = numBins
        self.stripPitch = stripPitch
        self.numEvents = np.zeros(self.numStrips*2-4)
        self.numGoodEvents = 0
        self.numBadEvents = 0
        self.energyCal = np.ones((self.numStrips*2-4))
        self.minHeight = minHeight

        self.dt = np.dtype([('pulseHeights',np.int32,(self.numStrips,)),
                ('regionMain',np.int8),
                ('regionSec',np.int8),
                ('ratioMain',np.float64),
                ('ratioSec',np.float64),
                ('t',np.uint32),
                ('x',np.float32),
                ('E',np.float64),
                ('isGood',np.bool_)])

        #self.allEvents = np.ndarray((0,),dtype=self.dt)
        self.allEvents = []

        self.goodEvents = np.ndarray((0,),dtype=self.dt)

    def addEvents(self, eventArray = None):

        ''' Usage: addEvent(eventArray = None)

            Provide a numpy masked array with the dtype matching the dtype defined
            in this object. '''

        if eventArray is None or eventArray.dtype != self.dt:

            print "You did not provide a valid array! \n\n"

        else:

            for event in eventArray:

                self.allEvents.append(event)

                check1 = np.floor(event['ratioMain']*100.)<self.numBins-1
                check2 = event['ratioMain']>=1.
                #check3 = np.argmax(event['pulseHeights'])
                check4 = np.max(event['pulseHeights'])>self.minHeight

                if check1 and check2 and check4 and event['isGood']:

                    region = event['regionMain']
                    
                    ratioBin = np.floor(event['ratioMain']*100.)

                    self.rhist[region][ratioBin] += 1

                    self.numGoodEvents += 1

                    self.numEvents[region] += 1

                else:

                    self.allEvents[-1]['isGood'] = False
                    self.numBadEvents += 1

    def callParser(self,fname=None,folderName=None):

        '''
        File: calibrationClass.py
        Author: Anders Priest
        Description: Use this function to load raw data from binary files,
            either from a single file or from a set of files from a directory.
            If a directory name is given, all .bin files from that directory
            will be loaded, and other files will be ignored. If the name of a
            file and the name of a folder are given, this will result in an
            error. The specified folder must be in the current working
            directory.
        '''

        if fname is not None and folderName is not None:

            print "You cannot provide both a file name and a folder name!\n"
            return 1

        import pixieBinParser as pp

        if fname is not None:

            print "Reading ", fname, "..."
            prsr = pp.pixieParser(fname=fname,moduleNum=self.moduleNum,
                                  channelNum=self.channelNum, 
                                  minheight=self.minHeight)

            if fname[-3:] == 'bin':
                prsr.readBinFile()
            else:
                prsr.readTextFile()

            eventList = prsr.makeAndWriteEvents()

            self.addEvents(eventList)

            print "Done!\n"

        elif folderName is not None:

            import os

            curDir = os.getcwd()

            fileDir = curDir + '/' + folderName

            eventList = []

            fileList = os.listdir(fileDir)
            fileList.sort()

            for thisFile in fileList:

                if thisFile[-4:] == '.bin' or thisFile[-4:] == '.txt':

                    print "Reading ", thisFile, "..."
                    prsrPath = folderName + '/' + thisFile
                    prsr = pp.pixieParser(fname=prsrPath,
                                         moduleNum=self.moduleNum,
                                         channelNum=self.channelNum,
                                         minHeight=self.minHeight)
                    if thisFile[-3:] == 'bin':
                        prsr.readBinFile()
                    else:
                        prsr.readTextFile()
                    eventList = prsr.makeAndWriteEvents()

                    self.addEvents(eventList)

                    del prsr
                    print "Done!\n"

                else:

                    print "Skipping ", thisFile, ", because it is not a \
                        .bin or .txt file..."

            print "Done!\n"

        else:

            print "You didn't specify anything!\n"
            return 1

        self.updateMap()

    def plotMap(self, regions = None):

        '''Usage: plotMap(region = None)

        region(int): If region is provided, only the mapping for the region
            provided will be mapped. Otherwise, all regions will be plotted.

        Simply plots the mapping for the region given or for all regions.

        *** Does not need event type update. *** '''

        if regions == None:

            # Plots the current mapping between ratio and position for all
            # regions

            print "Plotting map for all regions...\n"

            fig = plt.figure()
            ax = fig.add_subplot(111)

            for region, ratioMap in enumerate(self.mapping):

                lineName = "  Region " + str(region)
                ax.plot(ratioMap,self.WPx[region],
                        label=lineName, color=colors[region])

            # Shrink current axis's height by 10% on the bottom
            box = ax.get_position()
            ax.set_position([box.x0, box.y0 + box.height * 0.1,
                                 box.width, box.height * 0.9])

            plt.ylabel('Ratio',fontsize=16)
            plt.xlabel('Position within region',fontsize=16)

            plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))

            for tick in ax.xaxis.get_major_ticks():
                tick.label.set_fontsize(16)
            for tick in ax.yaxis.get_major_ticks():
                tick.label.set_fontsize(16)

            plt.show()

        else:

            # Plots the current mapping between ratio and position for the
            # region listed

            print "Plotting map for regions ", regions, "...\n"

            fig = plt.figure()
            ax = fig.add_subplot(111)

            for i,region in enumerate(regions):
                lineName = "  Region " + str(region)
                ax.plot(self.mapping[region,:],self.WPx[region],label=lineName,
                        color=colors[region])

            # Shrink current axis's height by 10% on the bottom
            box = ax.get_position()
            ax.set_position([box.x0, box.y0 + box.height * 0.1,
                                 box.width, box.height * 0.9])

            plt.ylabel('Ratio',fontsize=16)
            plt.xlabel('Position within region',fontsize=16)

            plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))

            for tick in ax.xaxis.get_major_ticks():
                tick.label.set_fontsize(16)
            for tick in ax.yaxis.get_major_ticks():
                tick.label.set_fontsize(16)

            plt.show()

    def plotWPs(self, masked=0):

        fig = plt.figure()
        ax = fig.add_subplot(111)

        # Plotting the weighting potentials across space

        for region,wp_r in enumerate(self.WP):
            WPname = " Region " + str(region)
            if region % 2 == 0:
                ax.plot(np.linspace(0,self.stripPitch/2.,
                        len(wp_r))+np.ones((len(wp_r)))*region*self.stripPitch/2.,wp_r,
                        label=WPname, color=colors[region])
            else:
                ax.plot(np.linspace(0,self.stripPitch/2.,
                        len(wp_r))+np.ones((len(wp_r)))*region*self.stripPitch/2.,wp_r[::-1],
                        label=WPname, color=colors[region])

        # Shrink current axis's height by 10% on the bottom
        box = ax.get_position()
        ax.set_position([box.x0, box.y0 + box.height * 0.1,
                             box.width, box.height * 0.9])

        plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
        plt.ylabel('Weighting Potential',fontsize=16)
        plt.xlabel('Position (mm)',fontsize=16)

        ax.set_ylim([0,1.5])

        for tick in ax.xaxis.get_major_ticks():
            tick.label.set_fontsize(16)
        for tick in ax.yaxis.get_major_ticks():
            tick.label.set_fontsize(16)

        plt.show()

    def mapEvent(self, e = None, xOnly = 0, EOnly = 0, x = None):

        '''Usage: mapEvent(e = None)

        e(event object): Event instance to be mapped. The event position will
            be added to the attributes of the event instance.

        Take in an event and use the current mapping to reconstruct the
        position of the event

        For the love of god, take the print statements out before trying
        to use this for realsies'''

        if e == None:

            print "Please provide a valid event of class type 'event'!\n"

        else:

            if xOnly == 0 and EOnly == 0:
                xOnly = 1
                EOnly = 1
                both = 1
            elif xOnly == 1 and EOnly == 1:
                both = 1
            else:
                both = 0

            if xOnly == 1:
                for i,x in enumerate(self.WPx):
                    if x == e['regionMain']*self.stripPitch/2.:
                        break

                if e['regionMain']%2 == 0:
                    for j,ratio in enumerate(self.mapping[event['regionMain']][i:]):
                        if e['ratioMain'] < ratio:
                            e['x'] = 
                    

                if both == 0:
                    return e['x']

            if EOnly == 1:
                energy = np.max(e['pulseHeights'])/self.mapXtoWP(e=e) * \
                    self.energyCal

                if both == 0:
                    return energy

            return [e['x'],energy]

    def mapXtoWP(self,e=None):

        '''
        File: calibrationClass.py
        Author: Anders Priest
        Description: Maps position to the reconstructed weighting potential for
            the region where the interaction occurred.
        '''
        if e is not None:
            #return self.WP[e['regionMain'],round(e['x']/ \
            #        self.stripPitch*float(np.shape(self.WP)[1]))]
            for WPbin,WPpos in enumerate(self.WPx):
                if e['x'] < WPpos:
                    break
            return self.WP[e['regionMain']][WPbin]
        
        else:
            print "You need to provide a position to map a weighting potential\
                to!"
            return 0

    def energyCalibration(self):

        print "Using good events to reconstruct the energy calibration..."
        energies = []

        for i,event in enumerate(self.allEvents):

            if event['isGood']:
                event['E'] = self.mapEvent(event,EOnly=1)
                energies.append(event['E'])

        print "The number of events used for this energy calibration: ", len(energies)

        Ehist,EbinEdges = np.histogram(energies,bins=1000,
                range=(0,max(energies)))

        histMax = np.argmax(Ehist)

        self.Ehist,self.EbinEdges = np.histogram(energies,bins=1000,
                range=(0,EbinEdges[histMax+100]))

        histMax = np.argmax(self.Ehist)
        
        self.energyCal = 59.5/((self.EbinEdges[histMax+1]+self.EbinEdges[histMax])/2.)

        self.EbinEdges = self.EbinEdges*self.energyCal

        print "Done!\n\n"

    def plotEnergyCal(self):

        ''' *** Does not need event type update. *** '''

        fig = plt.figure()
        ax = fig.add_subplot(111)

        EbinCenters = (self.EbinEdges[1:]+self.EbinEdges[:-1])/2.
        ax.step(EbinCenters,self.Ehist,color=colors[0])

        # Shrink current axis's height by 10% on the bottom
        box = ax.get_position()
        ax.set_position([box.x0, box.y0 + box.height * 0.1,
                             box.width, box.height * 0.9])

        plt.ylabel('Counts',fontsize=16)
        plt.xlabel('Energy (keV)',fontsize=16)

        for tick in ax.xaxis.get_major_ticks():
            tick.label.set_fontsize(16)
        for tick in ax.yaxis.get_major_ticks():
            tick.label.set_fontsize(16)
        
        plt.show()

    def gatherPositions(self,regions=None,fnames=None):

        positions = []

        if regions is not None:

            for i,region in enumerate(regions):

                positions.append([])

                for event in self.allEvents:

                    if event['isGood'] and event['regionMain'] == region:

                        if event['regionMain']%2 == 0:
                            positions[i].append(event['x'] + 
                                    (np.argmax(event['pulseHeights'])-1.)*self.stripPitch)
                        else:
                            positions[i].append(np.argmax(event['pulseHeights'])*self.stripPitch
                                    - event['x'])

        elif fnames is not None:

            import pixieBinParser as pp
            for i,fileName in enumerate(fnames):

                positions.append([])

                filePath = fileName
                prsr = pp.pixieParser(fname=filePath,moduleNum=self.moduleNum,
                                      channelNum=self.channelNum,minHeight=self.minHeight)

                prsr.readBinFile()

                eventList = prsr.makeAndWriteEvents()
                
                for event in eventList:

                    check1 = np.floor(event['ratioMain']*100.) < self.numBins-1
                    check2 = event['ratioMain'] >= 1.

                    if check1 and check2 and event['isGood']:

                        event['x'] = self.mapEvent(e=event,xOnly=True)

                        if event['regionMain']%2 == 0:
                            positions[i].append(event['x'] + 
                                    (np.argmax(event['pulseHeights'])-1.)*self.stripPitch)
                        else:
                            positions[i].append(np.argmax(event['pulseHeights'])*self.stripPitch
                                    - event['x'])

            return positions,eventList

        else:
            
            for event in self.allEvents:

                if event['isGood']:

                    if event['regionMain']%2 == 0:
                        positions.append(event['x'] + 
                                (np.argmax(event['pulseHeights'])-1.)*self.stripPitch)
                    else:
                        positions.append(np.argmax(event['pulseHeights'])*self.stripPitch
                                - event['x'])

        return positions

    def plotPositionHists(self,regions=None,fnames=None):

        fig = plt.figure()
        ax = fig.add_subplot(111)

        eventList = None
        
        if regions is not None:

            positions = self.gatherPositions(regions=regions)

            for i,region in enumerate(regions):

                histName = "Region " + str(region)

                hist,binEdges = np.histogram(positions[i],bins=1000,
                        range=(0.,self.stripPitch*(sum(self.channelNum)-2)))

                binCenters = (binEdges[1:]+binEdges[:-1])/2.
                
                ax.step(binCenters,hist,label=histName,
                        color=colors[i%len(colors)])

        elif fnames is not None:

            positions,eventList = self.gatherPositions(fnames=fnames)

            for i,fileName in enumerate(fnames):

                hist,binEdges = np.histogram(positions[i],bins=1000,
                        range=(0.,self.stripPitch*(sum(self.channelNum)-2)))

                binCenters = (binEdges[1:]+binEdges[:-1])/2.

                ax.step(binCenters,hist,label=fileName, 
                        color=colors[i%len(colors)])

        else:

            positions = self.gatherPositions()

            hist,binEdges = np.histogram(positions,bins=1000,
                    range=(0.,self.stripPitch*(sum(self.channelNum)-2)))
            
            binCenters = (binEdges[1:]+binEdges[:-1])/2.

            ax.step(binCenters,hist,label="All Events",color=colors[0])

        # Shrink current axis's height by 10% on the bottom
        box = ax.get_position()
        ax.set_position([box.x0, box.y0 + box.height * 0.1,
                             box.width, box.height * 0.9])

        plt.ylabel('Counts',fontsize=16)
        plt.xlabel('Position (mm)',fontsize=16)

        for tick in ax.xaxis.get_major_ticks():
            tick.label.set_fontsize(16)
        for tick in ax.yaxis.get_major_ticks():
            tick.label.set_fontsize(16)

        if fnames is not None:
            ncol = np.ceil(len(fnames)/4.)
        else:
            ncol = 1

        plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
        plt.show()

        if eventList is not None:
            return positions,eventList

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

    def readCalcWPs(self,fname = None,source = 'maxwell',path = None):

        '''Usage: readCalcWPs(fname = None, source = 'maxwell')

        fname is the file from which the weighting potentials will be read.

        source is the program that the weighting potejtials were output from. 
            since the file formats will be different, it is important to 
            indicate which format it will be.
        
        Read in calculated weighting potentials from Maxwell outputs or 
        from Igor written weighting potentials. These will be used for
        reconstructing position and energy using Method 1.'''

        import os

        self.WPFileName = fname

        self.WPs = []

        if source == 'maxwell':

            for i in range(sum(self.channelNum)):

                if fname[-5] != str(i)+'.fld':

                    fname.strip(fname[-5:])
                    fname += str(i) + '.fld'

                if path is not None:
                    fname = path+fname

                f = open(fname)   

                f.seek(0,os.SEEK_END)
                numbytes = f.tell()
                f.seek(0,os.SEEK_SET)

                f.readline()    # Informational Line
                f.readline()    # Informational Line

                while f.tell() < numbytes:

                    d = f.readline()

                    data = d.split()

                    x = float(data[0])
                    WP.append(float(data[-1]))

                self.WPs.append(WP)

            s0maxIndex = np.argmax(self.WPs[0])
            WPx = np.array(x) - np.ones(len(x))*self.WPs[0][s0maxIndex] \
                    - np.ones(len(x))*2.5

           self.mapping = []

           for i in range(sum(self.numChannels)-1):

                self.mapping.append([wp2/wp1 for wp1,wp2 in zip(self.WPs[i,i+1])])
                self.mapping.append([wp2/wp1 for wp1,wp2 in zip(self.WPs[i+1,i])])
