import serial
import time

class ServoController:
    def __init__(self):
        usbPort = '/dev/ttyACM0'
        self.sc = serial.Serial(usbPort, timeout=1)

    def closeServo(self):
        self.sc.close()

    def setAngle(self, n, angle):
        if angle > 180 or angle <0:
           angle=90
        byteone=int(254*angle/180)
        bud=chr(0xFF)+chr(n)+chr(byteone)
        self.sc.write(bytes(bud,'latin-1'))

    def setPosition(self, servo, position):
        position = int(position * 4)
        poslo = (position & 0x7f)
        poshi = (position >> 7) & 0x7f
        chan  = servo & 0x7f
        data =  chr(0xaa) + chr(0x0c) + chr(0x04) + chr(chan) + chr(poslo) + chr(poshi)
        self.sc.write(bytes(data,'latin-1'))

    def setSpeed(self, chan, speed):
        lsb = speed & 0x7f
        msb = (speed >> 7) & 0x7f
        cmd = chr(0x07) + chr(chan) + chr(lsb) + chr(msb)
        self.sc.write(bytes(cmd, 'latin-1'))

    def getPosition(self, servo):
        chan  = servo and 0x7f
        data =  chr(0xaa) + chr(0x0c) + chr(0x10) + chr(chan)
        self.sc.write(bytes(data,'latin-1'))
        w1 = ord(self.sc.read())
        w2 = ord(self.sc.read())
        return w1, w2

    def getErrors(self):
        data =  chr(0xaa) + chr(0x0c) + chr(0x21)
        self.sc.write(bytes(data,'latin-1'))
        w1 = ord(self.sc.read())
        w2 = ord(self.sc.read())
        return w1, w2

    def triggerScript(self, subNumber):
        data =  chr(0xaa) + chr(0x0c) + chr(0x27) + chr(0)
        self.sc.write(bytes(data,'latin-1'))
