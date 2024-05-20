from serial import Serial
import time
while True:
    with Serial('/dev/ttyAMA0', 115200) as serial:
        dataa = serial.readline()
        print(dataa)
        time.sleep(1)

