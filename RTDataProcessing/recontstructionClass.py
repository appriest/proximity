import calibrationClass as cc
import pixieBinParser as pp

class recon:

    def __init__(self, calibration=None):

        '''
        File: recontstructionClass.py
        Author: Anders Priest
        Description: This class should be used for mapping any number of events
            given a calibration object. The calibration will be used to map the
            events, both the positions and the energies, then store the data
            in histograms as well as in raw form.
        '''

        self.calibration = calibration

    def mapEvents(self, fname=None, folderName=None):

        if fname != None:

            prsr = pp.pixieParser(fname=fname,
                                moduleNum=self.calibration.moduleNum,
                                channelNum=self.calibration.channelNum)

            prsr.readBinFile()

            eventList = prsr.makeAndWriteEvents()

            for e in eventList:

                x = self.calibration.mapEvent(e=e)
