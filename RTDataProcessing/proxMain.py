import pixieBinParser as pp
import eventClass as ec
import calibrationClass as cc
import time

def analyzeData():

    start = time.time()
    cal = cc.calibration()
    cal.callParser(folderName='data')
    cal.reconstructWP()
    end = time.time()
    print "Elapsed time: ", end-start
    return cal

if __name__ == "__main__":

    analyzeData()
