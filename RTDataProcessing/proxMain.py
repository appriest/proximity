import pixieBinParser2 as pp
import eventClass as ec
import calibrationClass as cc

def analyzeData():

    cal = cc.calibration()
    cal.callParser(folderName='data')
    return cal

if __name__ == "__main__":

    analyzeData()
