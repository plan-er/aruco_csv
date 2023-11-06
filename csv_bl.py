import serial

data = serial.Serial('/dev/tty.ESP32-beacon-0',9600, timeout=3)

while True:
    line = data.readline()
    print(line)
    
data.close()
