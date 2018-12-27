import sys

import cv2
import numpy as np
from ImageData import ImageData
from CustomQLabel import CustomQLabel
from PyQt5 import QtCore,QtWidgets
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QDialog, QApplication, QWidget, QInputDialog, QLineEdit, QFileDialog
from PyQt5.uic import loadUi



class MainUI(QDialog):
  def __init__(self):
    super(MainUI,self).__init__()
    loadUi('mainUI.ui',self)
    self.image = None
    self.imageData = None
    self.kpImage = None
    self.scanned = False
    self.addedInterestPoint = False
    self.loadButton.clicked.connect(self.loadClicked)
    self.scanButton.clicked.connect(self.scanClicked)
    self.saveButton.clicked.connect(self.saveClicked)
    self.addButton.clicked.connect(self.addClicked)

  @pyqtSlot()
  def loadClicked(self):
    options = QFileDialog.Options()
    options |= QFileDialog.DontUseNativeDialog
    filename, _ = QFileDialog.getOpenFileName(self,"QFileDialog.getOpenFileName()", "", "Images (*.jpg *.png)",options=options)
    if filename:
      print(filename)
    self.loadImage(filename)
    self.scanButton.setEnabled(True)
    self.addButton.setEnabled(True)

  def addClicked(self):
    self.imgLabel.activate()

  def notifyAddedInterestPoint(self):
    self.addedInterestPoint=True
    if self.scanned:
      self.saveButton.setEnabled(True)

  def loadImage(self, fname):
    self.image=cv2.imread(fname)
    self.imgLabel = CustomQLabel(self.layoutWidget1)
    sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum)
    sizePolicy.setHorizontalStretch(0)
    sizePolicy.setVerticalStretch(0)
    self.imgLabel.setSizePolicy(sizePolicy)
    self.imgLabel.setFrameShape(QtWidgets.QFrame.Box)
    self.imgLabel.setAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignVCenter)
    self.displayImage()

  def displayImage(self):
    qformat = QImage.Format_Indexed8

    if len(self.image.shape)==3: #rows[0],cols[1],channels[2]
      if(self.image.shape[2])==4:
        qformat=QImage.Format_RGBA8888
      else:
        qformat=QImage.Format_RGB888
    img=QImage(self.image, self.image.shape[1],self.image.shape[0],self.image.strides[0],qformat)
    #BGR > RGB
    img=img.rgbSwapped()
    self.imgLabel.setPixmap(QPixmap.fromImage(img))
    self.imgLabel.adjustSize()
    self.imgLabel.setAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignVCenter)
    

  def scanClicked(self):
    orb = cv2.ORB_create()
    keypoints=orb.detect(self.image, None)
    keypoints, descriptors = orb.compute(self.image, keypoints)
    self.kpImage = cv2.drawKeypoints(self.image, keypoints, self.image, color=(0,255,0), flags=0)
    self.image = ImageData(keypoints, descriptors)
    self.displayScanedImage()
    self.scanned = True
    if self.addedInterestPoint:
      self.saveButton.setEnabled(True)

  def displayScanedImage(self):
    qformat = QImage.Format_Indexed8

    if len(self.kpImage.shape)==3: #rows[0],cols[1],channels[2]
      if(self.kpImage.shape[2])==4:
        qformat=QImage.Format_RGBA8888
      else:
        qformat=QImage.Format_RGB888
    img=QImage(self.kpImage, self.kpImage.shape[1],self.kpImage.shape[0],self.kpImage.strides[0],qformat)
    #BGR > RGB
    img=img.rgbSwapped()
    self.imgLabel.setPixmap(QPixmap.fromImage(img))
    self.imgLabel.setAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignVCenter)

  def saveClicked(self):
    self.imageData=self.image
    self.imageData.setInterestPoints(self.imgLabel.rectangles)
    print(self.imageData.kp)
    print(self.imageData.desc)
    print(self.imageData.ipoints)
    
 


app=QApplication (sys.argv)
window=MainUI()
window.setWindowTitle('Tutorial')
window.show()
sys.exit(app.exec_())
