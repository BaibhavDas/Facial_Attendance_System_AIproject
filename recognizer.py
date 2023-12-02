import cv2
import os
import numpy as np
import time
import sys
import sqlite3 as sql

conn = sql.connect('database/database.db')
c = conn.cursor()

flag = 0
time_of_attendance = time.time()
face_cas = cv2.CascadeClassifier('cascades/haarcascade_frontalface_default.xml')
cap_video = cv2.VideoCapture(0)
recognizer = cv2.face.LBPHFaceRecognizer_create()
recognizer.read('trainer/trainer.yml')
font = cv2.FONT_HERSHEY_SIMPLEX
while True:
	ret, img = cap_video.read()
	gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
	faces = face_cas.detectMultiScale(gray, 1.3, 7)
	for (x,y,w,h) in faces:
		roi_gray = gray[y:y+h,x:x+w]
		cv2.rectangle(img, (x,y), (x+w,y+h), (255,0,0))
		id,conf = recognizer.predict(roi_gray)
		cv2.putText(img,str(id)+" "+str(conf),(x,y-10),font,0.55,(120,255,120),1)
		if(conf<80):
			for row in c.execute("SELECT * FROM students WHERE UID = ?",(str(id),)):
				if(str(id) == row[0]):
					c.execute("UPDATE students SET attendance= ? WHERE UID = ?",('Present',str(id)))
					conn.commit()
				else:
					os.system("python error_gui.py")
					flag = flag+1
					break;
	
	cv2.imshow('frame',img)	
	period = 20	
	if(flag == 10):
		os.system("python error_gui.py")
		break
	if(time.time()) > (time_of_attendance+period):
		break
	if(cv2.waitKey(100) & 0xFF == ord('q')):
		break


os.system("python Marking_attendance.py")

conn.close()
cap_video.release();
cv2.destroyAllWindows();
