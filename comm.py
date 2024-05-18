from serial import Serial

uart_read():
    with Serial('/dev/ttyUSB0', 115200) as serial:
        dataa = serial.readline()
        return dataa
        

