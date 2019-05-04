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
import numpy as np

class Pikama:

  firstFrame = None
  last_blobs = list()
  crop_coords = []
  cropping = False
  cropped  = False
  points = list()
  mirror_horizontal = False
  mirror_vertical = False
  fullScreen = False
  width = 500
  height = 500
  showHelp = True
  showBlobs = True
  need_snapshot = False
  
  def __init__(self, args=None):
    if args == None:
      ap = argparse.ArgumentParser()
      ap.add_argument("-v", "--video", help="path to the video file")
      ap.add_argument("-a", "--min-area", type=int, default=500, help="minimum area size")
      ap.add_argument("-A", "--max-area", type=int, default=10000, help="maximum area size")
      ap.add_argument("-t", "--threshold", type=int, default=20, help="video threshold")
      ap.add_argument("-d", "--debug-windows", type=bool, default=True, help="displays debug image windows")
      ap.add_argument("-f", "--fullscreen", nargs='?', const=False, help="displays debug window on full screen")
      args = vars(ap.parse_args())

    self.source = "file"
    if args.get("video", None) is None:
      self.vs = VideoStream(src=0).start()
      time.sleep(0.5)
     
    # otherwise, we are reading from a video file
    else:
      self.source = "camera"
      self.vs = cv2.VideoCapture(args["video"])
      self.vs.set(cv2.CAP_PROP_FPS, 5)
     
    # initialize the first frame in the video stream
    self.firstFrame = None
    self.debugWindows = args["debug_windows"]
    self.fullScreen = args["fullscreen"] is False
    self.displayImageIndex = 0 #debug image
    self.min_area = args["min_area"] # blob minim size
    self.max_area = args["max_area"] # blob max size
    self.thval = args["threshold"]
    self.is_active = True
    self.showHelp = True
    self.showBlobs = True
    cv2.namedWindow("video", cv2.WINDOW_NORMAL | cv2.WINDOW_FREERATIO)
    if self.fullScreen:
      cv2.setWindowProperty("video", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
      self.showBlobs = False
      self.showHelp = False
      # cv2.resizeWindow("video", 1024, 768)
    else:
      cv2.setWindowProperty("video", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_NORMAL)
    cv2.setMouseCallback("video", self.click_and_crop)
    #  TODO : extraer width height y exponerlo

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
    frame = imutils.resize(frame, width=self.width)

    if self.cropped:
      newframe = frame[self.crop_coords[0][1]:self.crop_coords[1][1], self.crop_coords[0][0]:self.crop_coords[1][0]]
      # frame = None
      frame = imutils.resize(newframe, width=self.width)

    self.height, self.width, _ = frame.shape



    if self.mirror_horizontal:
      frame = cv2.flip( frame, 0 )
    if self.mirror_vertical:
      frame = cv2.flip( frame, 1 )

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (11, 11), 0)
   
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

    # self.displayImage is the image reference
    # local displayImage is the actual image
    self.displayImage = self.firstFrame
    if self.debugWindows:
      if self.displayImageIndex==0:
        displayImage = frame
      if self.displayImageIndex==1:
        displayImage = thresh
      if self.displayImageIndex==2:
        displayImage = frameDelta
   
    self.points = list()

    for c in cnts:
      area = cv2.contourArea(c)
      # if the contour is too small, ignore it
      if area < self.min_area:
        continue
      if area > self.max_area:
        continue

      # M = cv2.moments(c)
      # cX = int(M["m10"] / M["m00"])
      # cY = int(M["m01"] / M["m00"])

      (x,y),radius = cv2.minEnclosingCircle(c)
      x = int(x)
      y = int(y)
      center = (x,y)
      radius = int(radius)

      self.points.append([x,y,radius])

      if self.showBlobs:
        cv2.circle(displayImage, center, radius,(0,255,0),2)

    if self.fullScreen:
      cv2.setWindowProperty("video", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    else:
      cv2.setWindowProperty("video", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_NORMAL)

    if self.debugWindows:
      if self.showHelp:
        cv2.putText(displayImage,"blobs: "+str(len(self.points)),(10,13),cv2.FONT_HERSHEY_SIMPLEX, 0.4, (205, 250, 150), lineType=cv2.LINE_AA)
        cv2.putText(displayImage,"threshold: "+str(self.thval),(10,33),cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), lineType=cv2.LINE_AA)
        cv2.putText(displayImage,"min_area: "+str(self.min_area),(10,53),cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), lineType=cv2.LINE_AA)
        cv2.putText(displayImage,"max_area: "+str(self.max_area),(10,73),cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), lineType=cv2.LINE_AA)

        cv2.putText(displayImage,"1: threshold",(10,90),cv2.FONT_HERSHEY_SIMPLEX, 0.3, (155, 155, 155), lineType=cv2.LINE_AA)
        cv2.putText(displayImage,"2: min_size",(10,100),cv2.FONT_HERSHEY_SIMPLEX, 0.3, (155, 155, 155), lineType=cv2.LINE_AA)
        cv2.putText(displayImage,"3: max_size",(10,110),cv2.FONT_HERSHEY_SIMPLEX, 0.3, (155, 155, 155), lineType=cv2.LINE_AA)
        cv2.putText(displayImage,"space: REINICIA REFERENCIA",(10,120),cv2.FONT_HERSHEY_SIMPLEX, 0.3, (155, 155, 155), lineType=cv2.LINE_AA)
        cv2.putText(displayImage,"m: mirror horizontal",(10,130),cv2.FONT_HERSHEY_SIMPLEX, 0.3, (155, 155, 155), lineType=cv2.LINE_AA)
        cv2.putText(displayImage,"n: mirror vertical",(10,140),cv2.FONT_HERSHEY_SIMPLEX, 0.3, (155, 155, 155), lineType=cv2.LINE_AA)
        cv2.putText(displayImage,"r: reiniciar crop",(10,150),cv2.FONT_HERSHEY_SIMPLEX, 0.3, (155, 155, 155), lineType=cv2.LINE_AA)
        cv2.putText(displayImage,"mouse drag: crop",(10,160),cv2.FONT_HERSHEY_SIMPLEX, 0.3, (155, 155, 155), lineType=cv2.LINE_AA)
        cv2.putText(displayImage,"v: visuals",(10,170),cv2.FONT_HERSHEY_SIMPLEX, 0.3, (155, 155, 155), lineType=cv2.LINE_AA)
        cv2.putText(displayImage,"d: hide/show debug",(10,180),cv2.FONT_HERSHEY_SIMPLEX, 0.3, (155, 155, 155), lineType=cv2.LINE_AA)
        cv2.putText(displayImage,"q: salir",(10,190),cv2.FONT_HERSHEY_SIMPLEX, 0.3, (155, 155, 155), lineType=cv2.LINE_AA)

      if self.cropping:
        cv2.rectangle(displayImage, self.crop_coords[0], self.crop_coords[1], (200, 5, 5, 0.1), 2)

      # longest_side = max(self.width, self.height)
      # black = 255 * np.zeros((longest_side,longest_side,3), np.uint8)
      # cv2.imshow("video", black)
      cv2.imshow("video", displayImage)

    if self.need_snapshot: 
      cv2.imwrite('static/snapshot.jpg', displayImage)
      self.need_snapshot = False

    key = cv2.waitKey(10) & 0xFF

    # keyboard controls
    if key == ord("q"):
      self.is_active = False

    elif key == ord("r"):
      self.crop_coords = []
      self.cropped = False
      self.cropping = False
      self.firstFrame = None
    
    elif key == ord("m"):
      self.mirror_horizontal = not self.mirror_horizontal
      self.firstFrame = None
    elif key == ord("n"):
      self.mirror_vertical = not self.mirror_vertical
      self.firstFrame = None
    elif key == ord("f"):
      self.fullScreen = not self.fullScreen
    
    elif key == ord(" "):
      self.firstFrame = None
    
    elif key == ord("d"):
      self.debugWindows = not self.debugWindows
    elif key == ord("h"):
      self.showHelp = not self.showHelp
    elif key == ord("b"):
      self.showBlobs = not self.showBlobs
    
    elif key == ord("1"):
      self.thval+=10
    elif key == ord("2"):
      self.min_area+=100
    elif key == ord("3"):
      self.max_area+=500

    elif key == ord("v"):
      self.displayImageIndex+=1
 
    if self.displayImageIndex>2:
      self.displayImageIndex=0

    if self.thval > 190:
      self.thval=0
    if self.min_area > 2500:
      self.min_area=100
    if self.max_area > 15000:
      self.max_area=5000


    self.points.append ( [self.width, self.height] )
    return self.points
    # if self.last_blobs != points:
    #   self.last_blobs == points
    #   return points

  def stop(self):
    # cleanup the camera and close any open windows
    self.vs.stop() #if self.source=="camera" else self.vs.release()
    cv2.destroyAllWindows()
    # raise SystemExit()


  def click_and_crop(self, event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
      self.crop_coords = [(x, y), (x, y)]
      self.cropping = True
      self.cropped = False
   
    elif event == cv2.EVENT_LBUTTONUP:
      # x = max(x, self.crop_coords[0][0]+50)
      # y = max(y, self.crop_coords[0][1]+50)
      self.crop_coords[1] = (x, y)
      self.cropped = True

      if abs(x-self.crop_coords[0][0]) < 100 or abs(y-self.crop_coords[0][1]) < 100:
        self.crop_coords = []
        self.cropped = False
      
      self.cropping = False
      self.firstFrame = None

    if self.cropping and not self.cropped:
      self.crop_coords[1] = (x, y)

 

if __name__ == '__main__':
  pikama = Pikama(None)

  cnt = 0

  while pikama.is_active:
    blobs = pikama.search_blobs()
    # if blobs != None:
    #   if len(blobs)>1 :
    #     print (blobs)
    #     break
  
  raise SystemExit()
