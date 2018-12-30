import sys
import os

import cv2
import numpy as np

from ImageData import ImageData
from PyQt5 import QtCore
from PyQt5.QtWidgets import QDialog, QFileDialog
from PyQt5.QtCore import pyqtSlot
from PyQt5.uic import loadUi





class ImageUI(QDialog):
  def __init__(self):
    super(ImageUI,self).__init__()
    loadUi('addImage.ui',self)
    self.imgByteArray = []

    if len(self.imgByteArray) == 0:
      self.closeButton.setDisabled(True)
      self.setWindowFlag(QtCore.Qt.WindowCloseButtonHint, False)
      self.noImg = True
    self.addImgButton.clicked.connect(self.addClicked)
    self.closeButton.clicked.connect(self.closeClicked)

  @pyqtSlot()
  def addClicked(self):
    options = QFileDialog.Options()
    options |= QFileDialog.DontUseNativeDialog
    filename, _ = QFileDialog.getOpenFileName(self,"QFileDialog.getOpenFileName()", "", "Images (*.jpg *.png)",options=options)
    with open(filename, "rb") as imageFile:
        f = imageFile.read()
        self.imgByteArray.append(bytearray(f))
        print("New image added to interest point: "+ filename)
    if self.noImg == True:
      self.noImg= False
      self.closeButton.setDisabled(False)

  def closeClicked(self):
    self.close()