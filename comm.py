from serial import Serial
import time
import re

def UARTRead():
    with Serial('/dev/ttyACM0', 115200) as serial:
        dataa = serial.readline()
        print(dataa)
        pattern = r'(\d+)\s+(\d+)'
        match = re.search(pattern, dataa)
        return match
