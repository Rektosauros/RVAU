import sys

import cv2
import numpy as np

class Image:
  def __init__(self, keypoints, descriptors):
    super(Image,self).__init__()
    self.kp = keypoints
    self.desc = descriptors

