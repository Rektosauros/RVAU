from PyQt5.QtWidgets import QLabel,QApplication,QFileDialog
from InterestPoint import InterestPoint
from addImageUI import ImageUI

import PyQt5.QtCore as QtCore
import PyQt5.QtGui as QtGui 


class Rectangle:
    def __init__(self,point1,point2):
        self.begin=point1
        self.end=point2
        print(str(point1),str(point2))
    def __str__(self):
        return "Begin:" + str(self.begin) + " End:" + str(self.end)

class CustomQLabel(QLabel):
    def __init__(self,parent):
        super().__init__(parent)
        self.setMouseTracking(True)
        self.begin = QtCore.QPoint()
        self.end = None
        self.pressed = False
        self.inside = False
        self.active = False
        self.rectangles = []
        self.interestPoints = []
        self.show()

    # Activate rectangle drawing mode
    def activate(self):
        self.active=True
        QApplication.setOverrideCursor(QtCore.Qt.CrossCursor)

    # Deactivate rectangle drawing mode
    def deactivate(self,active):
        self.active=active
        self.pressed=False
        self.begin = None
        self.end = None

    def emptyData(self):
        self.rectangles=[]
        self.interestPoints=[]

    # Draw rectangles on every frame
    def paintEvent(self, event):
        super(CustomQLabel, self).paintEvent(event)
        qp = QtGui.QPainter(self)
        br = QtGui.QBrush(QtGui.QColor(100, 10, 10, 40))  
        qp.setBrush(br) 
        if self.pressed and self.end is not None:
            qp.drawRect(QtCore.QRect(self.begin, self.end)) 
        for rec in self.rectangles :
            qp.drawRect(QtCore.QRect(rec.begin, rec.end))       

    # Start drawing rectangle on mouse press by defining first rectangle point
    def mousePressEvent(self, event):
        if self.inside and self.active: 
            self.begin = event.pos()
            self.pressed=True
            self.update()

    # Update the rectangle second point's coordinates as the mouse moves
    def mouseMoveEvent(self, event):
        if self.pressed:
            self.end = event.pos()
            self.update()

    # Finish the creation of the rectangle on mouse release and show dialogues to add info to new interest point
    def mouseReleaseEvent(self, event):
        if self.inside and self.active and self.pressed:
            self.rectangles.append(Rectangle(self.begin,self.end))
            interestPoint = InterestPoint(self.begin.x(),self.end.x(),self.begin.y(),self.end.y())
            self.parent().parent().notifyAddedInterestPoint()
            self.deactivate(False)
            QApplication.setOverrideCursor(QtCore.Qt.ArrowCursor)
            self.update()
            self.imageUi = ImageUI()
            self.imageUi.exec_()
            interestPoint.imagesArray=self.imageUi.image
            interestPoint.InterestPointName = self.imageUi.IPName
            self.interestPoints.append(interestPoint)
            print(interestPoint.InterestPointName)

    # Mouse enters the drawing area
    def enterEvent(self, event):
        QLabel.enterEvent(self, event)
        self.pressed=False
        self.inside=True
           
    # Mouse leaves the drawing area
    def leaveEvent(self, event):
        QLabel.leaveEvent(self, event)
        self.deactivate(self.active)
        self.inside=False
       
        