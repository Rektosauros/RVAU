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
    self.database = []
    self.descriptors = None
    self.keypoints = None
    self.kpImage = None
    self.scanned = False
    self.addedInterestPoint = False
    self.loadButton.clicked.connect(self.newImageClicked)
    self.scanButton.clicked.connect(self.scanClicked)
    self.saveButton.clicked.connect(self.saveClicked)
    self.saveDBButton.clicked.connect(self.saveDBClicked)
    self.addButton.clicked.connect(self.addClicked)

  @pyqtSlot()
  def newImageClicked(self):
    options = QFileDialog.Options()
    options |= QFileDialog.DontUseNativeDialog
    filename, _ = QFileDialog.getOpenFileName(self,"Find Image", "", "Images (*.jpg *.png)",options=options)
    if filename:
      self.imageName = os.path.splitext(os.path.basename(filename))[0]
    self.loadImage(filename)
    self.saveDBButton.setEnabled(False)
    self.scanButton.setEnabled(True)
    self.addButton.setEnabled(True)

  def addClicked(self):
    self.imgLabel.activate()

  def notifyAddedInterestPoint(self):
    self.addedInterestPoint=True
    if self.scanned:
      self.saveButton.setEnabled(True)

  # Load image into the program
  def loadImage(self, fname):
    self.scanned=False
    self.addedInterestPoint=False
    self.image=cv2.imread(fname)
    self.imgLabel = CustomQLabel(self.layoutWidget1)
    sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum)
    sizePolicy.setHorizontalStretch(0)
    sizePolicy.setVerticalStretch(0)
    self.imgLabel.setSizePolicy(sizePolicy)
    self.imgLabel.setFrameShape(QtWidgets.QFrame.Box)
    self.imgLabel.setAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignVCenter)
    self.displayImage()

  # Display loaded image on gui
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
    
  # Get Keypoint and Descriptors of the image
  def scanClicked(self):
    sift = cv2.xfeatures2d.SIFT_create()
    self.keypoints, self.descriptors =  sift.detectAndCompute(self.image,None)
    self.kpImage = cv2.drawKeypoints(self.image, self.keypoints, self.image, color=(0,255,0), flags=0)
    self.displayScannedImage()
    self.scanned = True
    if self.addedInterestPoint:
      self.saveButton.setEnabled(True)

  # Display the image with the scanned keypoints drawn
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

  # Add an image alongside it's scanned features and interest points to database
  def saveClicked(self):
    imageData = ImageData(self.keypoints, self.descriptors, self.image)
    imageData.setInterestPoints(self.imgLabel.interestPoints)
    index=[]
    for point in imageData.kp:
      temp=(point.pt, point.size, point.angle, point.response, point.octave, point.class_id)
      index.append(temp)
    imageData.kp=index
    self.database.append(imageData)
    self.saveDBButton.setEnabled(True)
    self.restartView()

  def restartView(self):
    self.image = None
    self.kpImage = None
    self.imgLabel.emptyData()
    self.imgLabel.setPixmap(QPixmap(1,1))
    self.scanned = False
    self.addedInterestPoint = False
    self.scanButton.setEnabled(False)
    self.addButton.setEnabled(False)
    self.saveButton.setEnabled(False)

  # Save database to pickle
  def saveDBClicked(self):
    outfile=open('databaseAR','wb')
    pickle.dump(self.database, outfile)
    outfile.close()
    
def main():
  app=QApplication (sys.argv)
  window=MainUI()
  window.setWindowTitle('AR Preparation Tool')
  window.show()
  sys.exit(app.exec_())

if __name__ == '__main__':
    main()  

