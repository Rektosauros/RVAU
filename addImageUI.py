import sys
import os

import cv2
import numpy as np

from ImageData import ImageData
from PyQt5 import QtCore
from PyQt5.QtWidgets import QDialog, QFileDialog, QMessageBox
from PyQt5.QtCore import pyqtSlot
from PyQt5.uic import loadUi





class ImageUI(QDialog):
  def __init__(self):
    super(ImageUI,self).__init__()
    loadUi('addImage.ui',self)
    self.image = []
    self.imgNames = []
    if len(self.image)==0:
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
    if self.imgNameLineEdit.text() == "":
      QMessageBox.question(self, "Message", "insert an image name to add a new image to the interest point", QMessageBox.Ok, QMessageBox.Ok)
    else:
      print(self.imgNameLineEdit.text())
      self.imgNames.append(self.imgNameLineEdit.text())
      self.image.append(cv2.imread(filename))
      print("New image added to interest point: "+ filename)
      self.imgNameLineEdit.setText("")
    if self.noImg == True:
      self.noImg= False
      self.closeButton.setDisabled(False)

  def closeClicked(self):
    self.close()
