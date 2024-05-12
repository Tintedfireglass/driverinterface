from serial import Serial

uart_read():
    with Serial('/dev/ttyUSB0', 9600) as serial:
        serial.send('Apple pie')
        answer = serial.readline()
        return answer
        

