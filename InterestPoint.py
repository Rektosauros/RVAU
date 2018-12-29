import sys

import cv2
import numpy as np

class InterestPoint:
  def __init__(self, ipoint):
    self.ipoint = ipoint
    self.imagesByteArray = []

  def addImage(self,image):
    self.imagesByteArray.append(image)
  



