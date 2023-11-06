import serial
import threading
import cv2
import cv2.aruco as aruco
import numpy as np
import pandas as pd
import csv
import time


# シリアルポートからのデータ読み取りを行う関数
def read_from_port(port, baudrate, data_queue):
    with serial.Serial(port, baudrate, timeout=1) as ser:
        print(f"Listening on {port}...")

        while True:
            if ser.in_waiting > 0:
                line = ser.readline().decode('utf-8').rstrip()
                try:
                    id, value = map(int, line.split(','))  # 受信データをカンマで分割して整数として解釈
                    data_queue.append((id, value))  # 受信データをキューに追加
                    print(f"{port} - ID: {id}, Value: {value}")
                except ValueError:
                    print(f"Invalid data received on {port}: {line}")


# CSVファイルにデータを書き込む関数
def write_to_csv(filename, data_queue):
    while True:
        if data_queue:
            with open(filename, 'a', newline='') as csvfile:
                csvwriter = csv.writer(csvfile)
                while data_queue:
                    csvwriter.writerow(data_queue.pop(0))
        time.sleep(1)  # 1秒ごとにチェック


# ESP32のCOMポートリスト
ports = ['/dev/tty.ESP32_BT_0', '/dev/tty.ESP32_BT_1', '/dev/tty.ESP32_BT_2']
baudrate = 115200
data_queue = []  # 受信データを保持するキュー

# CSVファイルを初期化
with open('data/num.csv', 'w', newline='') as csvfile:
    csvwriter = csv.writer(csvfile)
    csvwriter.writerow(['id', 'figure'])  # ヘッダーの書き込み

# シリアル通信のスレッドを起動
threads = []
for port in ports:
    t = threading.Thread(target=read_from_port, args=(port, baudrate, data_queue))
    threads.append(t)
    t.start()

# CSV書き込みスレッドを起動
csv_thread = threading.Thread(target=write_to_csv, args=('data/num.csv', data_queue))
csv_thread.start()

# 以下はカメラ処理のコード
targetVideo = 0
cap = cv2.VideoCapture(targetVideo)
aruco_dict = aruco.getPredefinedDictionary(aruco.DICT_4X4_50)

while cap.isOpened():
    ret, frame = cap.read()
    if frame is None:
        break

    # アルコマーカーの検出
    parameters = aruco.DetectorParameters()
    corners, ids, _ = aruco.detectMarkers(frame, aruco_dict, parameters=parameters)
    frame = aruco.drawDetectedMarkers(frame, corners, ids)

    # マーカーが検出されたら、CSVファイルからデータを読み込んで表示
    if ids is not None:
        df = pd.read_csv('data/num.csv')
        for i in range(len(ids)):
            marker_id = ids[i][0]
            if marker_id in df['id'].values:
                text = str(df[df['id'] == marker_id].iloc[-1]['figure'])
            else:
                text = str(marker_id)

            c = corners[i][0]
            x = int(np.mean(c[:, 0]))
            y = int(np.mean(c[:, 1]))
            cv2.putText(frame, text, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 0), 3)

    cv2.imshow('frame', frame)

    if not ret or cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

# スレッドの終了を待つ
for t in threads:
    t.join()
csv_thread.join()
