import sys

import cv2
import numpy as np

class InterestPoint:
  def __init__(self, x1,x2,y1,y2):
    self.x1=x1
    self.x2=x2
    self.y1=y1
    self.y2=y2
    self.imagesArray = []

  def __str__(self):
      return "Interest Point at rectangle: "+"("+str(self.x1)+","+str(self.y1)+"), ("+str(self.x2)+","+str(self.y2)+") - with "+str(len(self.imagesArray))+" images"

  def addImage(self,image):
    self.imagesArray.append(image)

  
  



