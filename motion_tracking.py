from imutils.video import VideoStream
import argparse
import datetime
import imutils
import time
import cv2
import numpy as np


room_status = []
entrance_count = 0
ap = argparse.ArgumentParser()
#ap.add_argument("", "--video", help="path to the video file")
ap.add_argument("-a", "--min-area", type=int, default=1000, help="minimum area size")
args = vars(ap.parse_args())

if args.get("video", None) is None:
	vs = VideoStream(src=0).start()
	time.sleep(3.0)

firstFrame = None #contains original image to compare too


while True:

    frame = vs.read()
    frame = frame if args.get("video", None) is None else frame[1]
    status = "Unoccupied"

    if frame is None:
	       break

    frame = imutils.resize(frame, width=500) #resize frame
    cframe = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    cframe = cv2.GaussianBlur(cframe, (21, 21), 0) #cframe is now the frame to be compared

#initialise comparison parameters
    if firstFrame is None:
        firstFrame = cframe
        mean_compare = cv2.mean(cframe)[0]
        continue

    diff_im = cv2.absdiff(cframe,firstFrame)
    binary_image = cv2.threshold(diff_im, 50, 255, cv2.THRESH_BINARY)[1] #thresholding operation

    thresh = cv2.dilate(binary_image, None, iterations=2) #fill holes
    cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)

    for c in cnts:
		# if the contour is too small, ignore it
        if cv2.contourArea(c) < args["min_area"]:
            continue

		# compute the bounding box for the contour, draw it on the frame,
		# and update the text
        (x, y, w, h) = cv2.boundingRect(c) #(x,y) are the top left corner and (w,h) are the width and height
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        status = "occupied"




    cv2.putText(frame,"Entrances: {}".format(entrance_count),(350,20),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
    cv2.putText(frame, "Room Status: {}".format(status), (10, 20),
		cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
    cv2.putText(frame, datetime.datetime.now().strftime("%A %d %B %Y %I:%M:%S%p"),(10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)
    cv2.imshow("binary image",frame)
    key = cv2.waitKey(1) & 0xFF


    room_status.append(status)

    if len(room_status) > 1:
        if room_status[-1] == "occupied" and room_status[-2] == "Unoccupied":
            entrance_count = entrance_count + 1
        print(room_status[-1],entrance_count)
