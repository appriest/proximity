import struct
import eventClass.event as event

class pixieParser:

    def __init__(self, fname=None):

        self.fname = fname

        if self.fname == None:

            print "Please enter a valid file name to properly initialize this class."

            return 0

        try:

            self.f = open(fname, 'rb')

        except IOError:

            print "The file you entered does not exist."

        print "Enter the number of channels in the system: "

        self.channels = raw_input()

        print "Enter the number of modules used for this data: "

        self.moduleNum = raw_input()
