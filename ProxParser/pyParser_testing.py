import binascii as ba

i=0
fname = "Proximity_scan_120814_0042.bin"
with open(fname, "rb") as f:
    byte = f.read(2)
    while byte != "":
        print ba.b2a_uu(byte)
        i += 1
        if i > 20:
            break
f.close()
