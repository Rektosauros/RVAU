import sys

import cv2
import numpy as np

class ImageData:
  def __init__(self, keypoints, descriptors, image):
    self.imageByteArray = image
    self.kp = keypoints
    self.desc = descriptors
    self.ipoints = []
  def setInterestPoints(self,rectangles):
    self.ipoints = rectangles
  



