import serial
import threading

# それぞれのESP32のCOMポートをリストとして定義
ports = ['/dev/tty.ESP32_BT_0', '/dev/tty.ESP32_BT_1', '/dev/tty.ESP32_BT_2']
baudrate = 115200


def read_from_port(port):
    ser = serial.Serial(port, baudrate, timeout=1)
    print(f"Listening on {port}...")

    try:
        while True:
            if ser.in_waiting > 0:
                line = ser.readline().decode('utf-8').rstrip()
                try:
                    id, value = map(int, line.split(','))  # 受信データをカンマで分割して整数として解釈
                    print(f"{port} - ID: {id}, Value: {value}")
                except ValueError:
                    print(f"Invalid data received on {port}: {line}")
    except KeyboardInterrupt:
        ser.close()


threads = []

for port in ports:
    t = threading.Thread(target=read_from_port, args=(port,))
    threads.append(t)
    t.start()

for t in threads:
    t.join()
