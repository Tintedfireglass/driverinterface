import spidev
import time

spi = spidev.SpiDev()
spi.open(5, 1)

def read_spi_data():
    spi.max_speed_hz = 1000000
    spi.bits_per_word = 8
    command_bytes = [0x01, 0x02, 0x03]  
    spi_response = spi.xfer(command_bytes)
    return spi_response

#
log_file_path = "spi_log.txt"

while True:
    spi_data = read_spi_data()
    with open(log_file_path, "a") as log_file:
        log_file.write(time.strftime("%Y-%m-%d %H:%M:%S") + ": " + str(spi_data) + "\n")
    time.sleep(1) 
