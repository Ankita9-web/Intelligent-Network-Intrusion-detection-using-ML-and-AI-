from imutils.video import VideoStream
import datetime
import imutils
import time
import cv2
import os

def video_feed():
	
	print("[INFO] starting video stream...")
	vs = cv2.VideoCapture(0)
	time.sleep(2.0)

	while True:
		# grab the frame from the threaded video stream and resize it to
		# have a maximum width of 400 pixels
		ret,frame = vs.read()

		cv2.imwrite('static/img/test.jpg',frame)

	
		imgencode=cv2.imencode('.jpg',frame)[1]
		stringData=imgencode.tostring()
		
		yield (b'--frame\r\n'
			b'Content-Type: text/plain\r\n\r\n'+stringData+b'\r\n')

		key = cv2.waitKey(1) & 0xFF
	
		# if the `q` key was pressed, break from the loop
		if key == ord("q"):
			break

	# close the output CSV file do a bit of cleanup
	print("[INFO] cleaning up...")
	csv.close()
	cv2.destroyAllWindows()
	vs.stop()
