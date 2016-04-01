import matplotlib.pyplot as plt
import numpy as np

def plotBox(vert=0.,offset=0.,regionLines=False):

    f = plt.figure()
    ax = f.add_subplot(111)

    ax.plot((2.0+offset,3.0+offset),(vert,vert),'k-')
    ax.plot((7.0+offset,8.0+offset),(vert,vert),'k-')
    ax.plot((12.0+offset,13.0+offset),(vert,vert),'k-')
    ax.plot((17.0+offset,18.0+offset),(vert,vert),'k-')
    ax.plot((22.0+offset,23.0+offset),(vert,vert),'k-')
    ax.plot((27.0+offset,28.0+offset),(vert,vert),'k-')

    ax.plot((2.0+offset,3.0+offset),(vert+vert/50.,vert+vert/50.),'k-')
    ax.plot((7.0+offset,8.0+offset),(vert+vert/50.,vert+vert/50.),'k-')
    ax.plot((12.0+offset,13.0+offset),(vert+vert/50.,vert+vert/50.),'k-')
    ax.plot((17.0+offset,18.0+offset),(vert+vert/50.,vert+vert/50.),'k-')
    ax.plot((22.0+offset,23.0+offset),(vert+vert/50.,vert+vert/50.),'k-')
    ax.plot((27.0+offset,28.0+offset),(vert+vert/50.,vert+vert/50.),'k-')

    ax.plot((2.0+offset,2.0+offset),(vert,vert+vert/50.),'k-')
    ax.plot((3.0+offset,3.0+offset),(vert,vert+vert/50.),'k-')
    ax.plot((7.0+offset,7.0+offset),(vert,vert+vert/50.),'k-')
    ax.plot((8.0+offset,8.0+offset),(vert,vert+vert/50.),'k-')
    ax.plot((12.0+offset,12.0+offset),(vert,vert+vert/50.),'k-')
    ax.plot((13.0+offset,13.0+offset),(vert,vert+vert/50.),'k-')
    ax.plot((17.0+offset,17.0+offset),(vert,vert+vert/50.),'k-')
    ax.plot((18.0+offset,18.0+offset),(vert,vert+vert/50.),'k-')
    ax.plot((22.0+offset,22.0+offset),(vert,vert+vert/50.),'k-')
    ax.plot((23.0+offset,23.0+offset),(vert,vert+vert/50.),'k-')
    ax.plot((27.0+offset,27.0+offset),(vert,vert+vert/50.),'k-')
    ax.plot((28.0+offset,28.0+offset),(vert,vert+vert/50.),'k-')

    if regionLines:

        ax.plot((0.0+offset,0.+offset),(0.0,vert+vert/50.),'k--')
        ax.plot((5.0+offset,5.0+offset),(0.0,vert+vert/50.),'k--')
        ax.plot((10.0+offset,10.0+offset),(0.0,vert+vert/50.),'k--')
        ax.plot((15.0+offset,15.0+offset),(0.0,vert+vert/50.),'k--')
        ax.plot((20.0+offset,20.0+offset),(0.0,vert+vert/50.),'k--')
        ax.plot((25.0+offset,25.0+offset),(0.0,vert+vert/50.),'k--')
        ax.plot((30.0+offset,30.0+offset),(0.0,vert+vert/50.),'k--')

    return ax
