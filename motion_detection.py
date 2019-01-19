# Detects movement from a reference frame
# cv2 chain: gray > gaussianblur >> absdiff > threshold > dilate > findcontours

# base code from pyimagesearch.com tutorials (Adrian Rosebrock)
# https://www.pyimagesearch.com/2015/05/25/basic-motion-detection-and-tracking-with-python-and-opencv/

# USAGE
# python motion_detector.py
# python motion_detector.py --video videos/example_01.mp4

# import the necessary packages
from imutils.video import VideoStream
import argparse
import datetime
import imutils
import threading
import time
import cv2
import math

from pythonosc import dispatcher
from pythonosc import osc_server
 
# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video", help="path to the video file")
ap.add_argument("-a", "--min-area", type=int, default=500, help="minimum area size")
ap.add_argument("-d", "--debug-windows", type=bool, default=True, help="displays debug image windows")
ap.add_argument("--ip", default="127.0.0.1", help="The ip to listen on")
ap.add_argument("--port", type=int, default=5005, help="The port to listen on")
args = vars(ap.parse_args())
 
# if the video argument is None, then we are reading from webcam
if args.get("video", None) is None:
  vs = VideoStream(src=0).start()
  time.sleep(2.0)
 
# otherwise, we are reading from a video file
else:
  vs = cv2.VideoCapture(args["video"])
 
# initialize the first frame in the video stream
firstFrame = None
debugWindows = args["debug_windows"]
showHelp = False
displayImageIndex = 0

def print_compute_handler(unused_addr, args, volume):
  try:
    print("[{0}] ~ {1}".format(args[0], args[1](volume)))
  except ValueError: pass

# OSC routes
dispatcher = dispatcher.Dispatcher()
dispatcher.map("/filter", print)
dispatcher.map("/logvolume", print_compute_handler, "Log volume", math.log)

server = osc_server.ThreadingOSCUDPServer( (args.get("ip",None), args.get("port",None)), dispatcher )
print("Serving on {}".format(server.server_address))
server_thread = threading.Thread(target=server.serve_forever)
server_thread.start()

# loop over the frames of the video
while True:
  # grab the current frame
  frame = vs.read()
  frame = frame if args.get("video", None) is None else frame[1]
 
  # if the frame could not be grabbed, then we have reached the end of the video
  if frame is None:
    break
 
  # resize the frame, convert it to grayscale, and blur it
  frame = imutils.resize(frame, width=500)
  gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
  gray = cv2.GaussianBlur(gray, (21, 21), 0)
 
  # if the first frame is None, initialize it
  if firstFrame is None:
    firstFrame = gray
    continue

  # compute the absolute difference between the current frame and first frame
  frameDelta = cv2.absdiff(firstFrame, gray)
  thresh = cv2.threshold(frameDelta, 25, 255, cv2.THRESH_BINARY)[1]
  # dilate the thresholded image to fill in holes, 
  thresh = cv2.dilate(thresh, None, iterations=2)
  # then find contours on thresholded image
  cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
    cv2.CHAIN_APPROX_SIMPLE)
  cnts = imutils.grab_contours(cnts)
 
  # loop over the contours
  for c in cnts:
    # if the contour is too small, ignore it
    if cv2.contourArea(c) < args["min_area"]:
      continue

    # compute the bounding box for the contour, draw it on the frame,
    (x, y, w, h) = cv2.boundingRect(c)

    if debugWindows:
      if displayImageIndex==0:
        displayImage = frame
      if displayImageIndex==1:
        displayImage = thresh
      if displayImageIndex==2:
        displayImage = frameDelta

      cv2.rectangle(displayImage, (x, y), (x + w, y + h), (0, 255, 0), 2)
      cv2.imshow("Video", displayImage)

  key = cv2.waitKey(1) & 0xFF

  # keyboard controls
  if key == ord("q"):
    break
  if key == ord("f"):
    firstFrame = None
  if key == ord("v"):
    displayImageIndex = 0 if displayImageIndex<3 else displayImageIndex+1
  if key == ord("d"):
    debugWindows = not debugWindows
  if key == ord("h"):
    showHelp = not showHelp
 
# cleanup the camera and close any open windows
server_thread.stop()
vs.stop() if args.get("video", None) is None else vs.release()
cv2.destroyAllWindows()