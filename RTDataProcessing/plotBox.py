import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

def plotBox(stripPitch=5.,stripNum=6,stripWidth=1.,vert=0.,offset=0.,regionLines=False):

    f = plt.figure()
    ax = f.add_subplot(111)

    pos = []

    for i in range(stripNum):
        ax.add_patch(patches.Rectangle((stripPitch*(0.5+i)+offset-stripWidth/2.,vert),
            stripWidth,vert/50.,facecolor="black"))

    if regionLines:

        for i in range(stripNum+2):
            ax.plot((stripPitch*i/2.+offset,stripPitch*i/2.+offset),(0.0,vert+vert/50.),'k--')

    return ax
