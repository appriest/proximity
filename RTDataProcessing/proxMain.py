import pixieBinParser2 as pp
import eventClass as ec
import calibrationClass as cc

def analyzeData():

    p1 = pp.pixieParser(fname="Prox_0075.bin",
                        moduleNum=2,channelNum=[4,4])

    p1.readBinFile()

    eventList = p1.makeAndWriteEvents()

    c1 = cc.calibration()

    for e in eventList:

        c1.addEvent(e)

    c1.calProperties()

    c1.updateMap()

if __name__ == "__main__":

    analyzeData()
