import sys

import cv2
import numpy as np

class InterestPoint:
  def __init__(self, x1,x2,y1,y2):
    self.pt1=[x1,y1]
    self.pt2=[x2,y2]
    self.center=[(x2+x1)/2,(y2+y1)/2]
    self.imagesArray = []
    self.InterestPointName = None

  def __str__(self):
      return "Interest Point at rectangle: "+str(self.pt1)+","+str(self.pt2)+" - with center at "+str(self.center)+" and with "+str(len(self.imagesArray))+" images"

  def addImage(self,image):
    self.imagesArray.append(image)

  
  



