import sys
import os

import cv2
import numpy as np
import pickle

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
    self.imageName = None
    self.imageData = None
    self.descriptors = None
    self.keypoints = None
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
      self.imageName = os.path.splitext(os.path.basename(filename))[0]
      print(self.imageName)
      with open(filename, "rb") as imageFile:
        f = imageFile.read()
        self.imgByteArray = bytearray(f)
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
    self.keypoints=orb.detect(self.image, None)
    self.keypoints, self.descriptors = orb.compute(self.image, self.keypoints)
    self.kpImage = cv2.drawKeypoints(self.image, self.keypoints, self.image, color=(0,255,0), flags=0)
    self.displayScannedImage()
    self.scanned = True
    if self.addedInterestPoint:
      self.saveButton.setEnabled(True)

  def displayScannedImage(self):
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
    self.imageData = ImageData(self.keypoints, self.descriptors, self.imgByteArray)
    self.imageData.setInterestPoints(self.imgLabel.interestPoints)
    outfile=open(self.imageName,'wb')
    index=[]
    for point in self.imageData.kp:
      temp=(point.pt, point.size, point.angle, point.response, point.octave, point.class_id)
      index.append(temp)
    self.imageData.kp=index
    pickle.dump(self.imageData, outfile)
    outfile.close()
    print(self.imageData.kp)
    print(self.imageData.desc)
    for ipoint in self.imageData.ipoints:
      print(ipoint)
    
 


app=QApplication (sys.argv)
window=MainUI()
window.setWindowTitle('AR Preparation Tool')
window.show()
sys.exit(app.exec_())
