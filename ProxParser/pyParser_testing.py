import struct

i=0
fname = "Proximity_scan_120814_0042.bin"
with open(fname, "rb") as f:
    byte = f.read(2)
    print struct.unpack('h',byte)
    while byte != "":
        byte = f.read(2)
        num, = struct.unpack('h',byte)
        print num
        i += 1
        if i > 100:
            break
f.close()
