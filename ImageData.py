import sys

import cv2
import numpy as np

class ImageData:
  def __init__(self, keypoints, descriptors):
    self.kp = keypoints
    self.desc = descriptors

  def setInterestPoints(self,rectangles):
    self.ipoints = rectangles
  



