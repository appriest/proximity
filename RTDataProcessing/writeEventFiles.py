import numpy as np
import os
import numpy.random as rand

def writeEvents(wpfile = None,n=0.0,source=None,numEvents=1000):

    WPs = []
    
    for i in range(8):
        
        stripchar = wpfile[-5]
        wpfile = wpfile.strip(stripchar+'.fld')

        wpfile = wpfile + str(i) + '.fld'

        pos,WP = readWPFile(wpfile)

        WPs.append(WP)

    maxWP = max(WP)
    noise = n/59.5/2.355

    if source is None:

        source = np.linspace(1.e-3,79.e-3,200)

    for sourcePos in source:

        sourcePos = round(sourcePos,6)
        posc = list(np.copy(pos))
        posc.append(sourcePos)
        poscSorted = np.argsort(posc)
        index = np.argmax(poscSorted)

        print index
        posWP = []
        if index-1>=0 and index<len(pos):
            xdata = [pos[index-1],pos[index]]
        else:
            continue
        
        for i in range(8):
            ydata = [WPs[i][index-1],WPs[i][index]]

            posWP.append(interpolateData(xdata,ydata,sourcePos))

        fname = 'events_n' + str(n).translate(None, '.') + '_pos' + \
                str(sourcePos).translate(None, '.') + '.txt'

        writeFile(posWP,noise,numEvents,fname,sourcePos,maxWP)

def interpolateData(xdata,ydata,x):

    if len(xdata) != 2 or len(ydata) != 2:

        print "Incorrect data structure given to interpolateData()..."
        return 0

    else:
        if x == xdata[0]:
            return ydata[0]
        elif x == xdata[1]:
            return ydata[1]
        else:
            return (ydata[1]-ydata[0])/(xdata[1]-xdata[0])*(x-xdata[0])+ydata[0]

def readWPFile(wpfile=None):

    if wpfile is not None:
        
        f = open(wpfile)

    else:

        print "You need to provide a WP file!\n\n"

    pos = []
    WPs = []

    f.seek(0, os.SEEK_END)
    numbytes = f.tell()

    f.seek(0)
    f.readline()
    f.readline()

    while f.tell() < numbytes:

        x = float(f.read(23))
        f.read(50)
        WP = float(f.read(23))
        f.readline()

        pos.append(x)
        WPs.append(WP)

    return [pos,WPs]

def writeFile(posWP,noise,numEvents,fname,sourcePos,maxWP):

    path = 'fabricatedData/' + fname
    f = open(path,'w+')

    print "Writing:  ", fname

    f.write('Source position: ')
    f.write(str(sourcePos))
    f.write(' mm\n')

    f.write('Noise level: ')
    f.write(str(noise*2.355*59.5/maxWP))
    f.write(' keV\n')

    for i in range(numEvents):

        event = []

        for j in range(len(posWP)):

            if noise>0:
                rand.seed()
                event.append(int(1000*(posWP[j] + rand.normal(scale=noise))))
            else:
                event.append(posWP[j])

            if event[-1]>=0:
                strEvent = str(round(event[-1],6))
            else:
                strEvent = str(round(event[-1],5))
            if len(strEvent)<8:
                for i in range(8-len(strEvent)):
                    strEvent = strEvent + '0'
            if j == len(posWP)-1:
                f.write(strEvent)
                break
            else:
                f.write(strEvent + '\t')

        f.write('\n')

    f.close()

    del f
