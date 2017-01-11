import matplotlib.pyplot as plt
import numpy as np

def plotSourcePos(ax,sourceNum,vert=180.,stepSize=0.127,diff=None):

    for source in sourceNum:

        x = 30.-source*stepSize
        if diff is not None:
            x = x-diff[-source]

        ax.plot((x,x),(vert+10,vert),'k')
        ax.plot((x,x+.1),(vert,vert+1.),'k')
        ax.plot((x-.1,x),(vert+1.,vert),'k')
        ax.text(x,vert+11.,'$\gamma$',fontsize=16,fontweight='bold')

    return ax
