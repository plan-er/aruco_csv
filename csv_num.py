import cv2
import cv2.aruco as aruco
import numpy as np
import pandas as pd
import csv_gen

targetVideo = 0

cap = cv2.VideoCapture(targetVideo)

mappingImg = "img/lenna-color.bmp"

aruco_dict = aruco.getPredefinedDictionary(aruco.DICT_4X4_50)

im_src = cv2.imread(mappingImg)

while cap.isOpened():
    ret, frame = cap.read()

    if frame is None:
        break

    parameters = aruco.DetectorParameters()
    corners, ids, _ = aruco.detectMarkers(frame, aruco_dict, parameters=parameters)
    frame = aruco.drawDetectedMarkers(frame, corners, ids)

    if np.all(ids != None):
        for i in range(len(ids)):
            marker_id = ids[i][0]
            c = corners[i][0]
            x = int(np.mean(c[:, 0]))
            y = int(np.mean(c[:, 1]))

            # マーカーIDに応じてテキストを表示

            csv_gen.generate('data/num.csv')

            df = pd.read_csv('data/num.csv')

            if marker_id == 0:
                text = str(df[df['id'] == 0].iloc[-1]['figure'])
            elif marker_id == 1:
                text = str(df[df['id'] == 1].iloc[-1]['figure'])
            elif marker_id == 2:
                text = str(df[df['id'] == 2].iloc[-1]['figure'])
            else:
                text = str(marker_id)

            # テキストを描画
            cv2.putText(frame, text, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 0), 3)

    cv2.imshow('frame', frame)

    if not ret:
        continue
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
