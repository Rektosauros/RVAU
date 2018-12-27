from PyQt5.QtWidgets import QLabel,QApplication
import PyQt5.QtCore as QtCore
import PyQt5.QtGui as QtGui 

class Rectangle:
    def __init__(self,point1,point2):
        self.begin=point1
        self.end=point2
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
        self.show()

    def activate(self):
        self.active=True
        QApplication.setOverrideCursor(QtCore.Qt.CrossCursor)

    def deactivate(self,active):
        self.active=active
        self.pressed=False
        self.begin = None
        self.end = None
           
    def paintEvent(self, event):
        super(CustomQLabel, self).paintEvent(event)
        qp = QtGui.QPainter(self)
        br = QtGui.QBrush(QtGui.QColor(100, 10, 10, 40))  
        qp.setBrush(br) 
        if self.pressed and self.end is not None:
            qp.drawRect(QtCore.QRect(self.begin, self.end)) 
        for rec in self.rectangles :
            qp.drawRect(QtCore.QRect(rec.begin, rec.end))       

    def mousePressEvent(self, event):
        if self.inside and self.active: 
            self.begin = event.pos()
            self.pressed=True
            self.update()

    def mouseMoveEvent(self, event):
        if self.pressed:
            self.end = event.pos()
            self.update()

    def mouseReleaseEvent(self, event):
        if self.inside and self.active and self.pressed:
            self.rectangles.append(Rectangle(self.begin,self.end))
            self.parent().parent().notifyAddedInterestPoint()
            print("New Interest point at:",self.begin,self.end)
            self.deactivate(False)
            QApplication.setOverrideCursor(QtCore.Qt.ArrowCursor)
            self.update()

    def enterEvent(self, event):
        QLabel.enterEvent(self, event)
        self.pressed=False
        self.inside=True
           

    def leaveEvent(self, event):
        QLabel.leaveEvent(self, event)
        self.deactivate(self.active)
        self.inside=False
       
        