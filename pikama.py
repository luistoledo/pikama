# Detects movement from a reference frame
# cv2 chain: gray > gaussianblur >> absdiff > threshold > dilate > findcontours

# base code from pyimagesearch.com tutorials (Adrian Rosebrock)
# https://www.pyimagesearch.com/2015/05/25/basic-motion-detection-and-tracking-with-python-and-opencv/

# USAGE
# python motion_detector.py # for camera
# python motion_detector.py --video videos/example_01.mp4 #from file

# import the necessary packages
from imutils.video import VideoStream
import argparse
import datetime
import imutils
import time
import sys
import cv2

class Pikama:
  
  def __init__(self, args=None):
    if args == None:
      ap = argparse.ArgumentParser()
      ap.add_argument("-v", "--video", help="path to the video file")
      ap.add_argument("-a", "--min-area", type=int, default=500, help="minimum area size")
      ap.add_argument("-t", "--threshold", type=int, default=20, help="video threshold")
      ap.add_argument("-d", "--debug-windows", type=bool, default=True, help="displays debug image windows")
      args = vars(ap.parse_args())

    self.source = "file"
    if args.get("video", None) is None:
      self.vs = VideoStream(src=0).start()
      time.sleep(0.5)
     
    # otherwise, we are reading from a video file
    else:
      self.source = "camera"
      self.vs = cv2.VideoCapture(args["video"])
      self.vs.set(cv2.cv.CV_CAP_PROP_FPS, 10)
     
    # initialize the first frame in the video stream
    self.firstFrame = None
    self.debugWindows = args["debug_windows"]
    self.displayImageIndex = 0 #debug image
    self.min_area = args["min_area"] # blob minim size
    self.thval = args["threshold"]
    self.is_active = True

  def stop(self):
    self.is_active = False

  def search_blobs(self):

    # grab the current frame
    frame = self.vs.read()
    frame = frame if self.source=="file" else frame[1]
   
    # if the frame could not be grabbed, then we have reached the end of the video
    if frame is None:
      return
   
    # resize the frame, convert it to grayscale, and blur it
    frame = imutils.resize(frame, width=500)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (21, 21), 0)
   
    # if the first frame is None, initialize it
    if self.firstFrame is None:
      self.firstFrame = gray
      return

    # compute the absolute difference between the current frame and first frame
    frameDelta = cv2.absdiff(self.firstFrame, gray)
    thresh = cv2.threshold(frameDelta, self.thval, 255, cv2.THRESH_BINARY)[1]
    # dilate the thresholded image to fill in holes, 
    thresh = cv2.dilate(thresh, None, iterations=2)
    # then find contours on thresholded image
    cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
      cv2.CHAIN_APPROX_SIMPLE) #TODO: optimizar búsqueda de Rects
    cnts = imutils.grab_contours(cnts)

    self.displayImage = self.firstFrame
    if self.debugWindows:
      if self.displayImageIndex==0:
        displayImage = frame
      if self.displayImageIndex==1:
        displayImage = thresh
      if self.displayImageIndex==2:
        displayImage = frameDelta
   
    points = list()

    for c in cnts:
      # if the contour is too small, ignore it
      if cv2.contourArea(c) < self.min_area:
        continue

      # M = cv2.moments(c)
      # cX = int(M["m10"] / M["m00"])
      # cY = int(M["m01"] / M["m00"])

      (x,y),radius = cv2.minEnclosingCircle(c)
      x = int(x)
      y = int(y)
      center = (x,y)
      radius = int(radius)

      points.append([x,y,radius])

      if self.debugWindows:
        cv2.circle(displayImage, center, radius,(0,255,0),2)

      # cv2.circle(displayImage, (cX, cY), 7, (255, 255, 255), -1)
      # cv2.circle(displayImage, (cX, cY), 7, (255, 255, 255), -1)

      # compute the bounding box for the contour, draw it on the frame,
      # (x, y, w, h) = cv2.boundingRect(c)

      # cv2.rectangle(displayImage, (x, y), (x + w, y + h), (0, 255, 0), 2)

    if self.debugWindows:
      cv2.putText(displayImage,"blobs: "+str(len(cnts)),(10,13),cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), lineType=cv2.LINE_AA)
      cv2.putText(displayImage,"threshold: "+str(self.thval),(10,33),cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), lineType=cv2.LINE_AA)
      cv2.putText(displayImage,"min_area: "+str(self.min_area),(10,53),cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), lineType=cv2.LINE_AA)

      cv2.imshow("video", displayImage)

    key = cv2.waitKey(1) & 0xFF

    # keyboard controls
    if key == ord("q"):
      self.is_active = False
    elif key == ord("v"):
      self.displayImageIndex+=1
      if self.displayImageIndex>2:
        self.displayImageIndex=0
    elif key == ord("f"):
      self.firstFrame = None
    elif key == ord("d"):
      self.debugWindows = not self.debugWindows
    elif key == ord("1"):
      self.thval+=10
    elif key == ord("2"):
      self.min_area+=100
    if self.thval > 190:
      self.thval=0
    if self.min_area > 2500:
      self.min_area=100

    return points

  def stop(self):
    # cleanup the camera and close any open windows
    self.vs.stop() #if self.source=="camera" else self.vs.release()
    cv2.destroyAllWindows()
    raise SystemExit()


if __name__ == '__main__':
  pikama = Pikama(None)

  cnt = 0

  while pikama.is_active:
    blobs = pikama.search_blobs()
    # if blobs != None:
    #   if len(blobs)>1 :
    #     print (blobs)
    #     break

