import cv2
import numpy as np
import pickle
from tkinter.filedialog import askopenfilename
import tkinter
from ImageData import ImageData


def getData():
    root = tkinter.Tk()
    root.withdraw()
    filename = askopenfilename(title = "Select Preparation Data")
    with open(filename, 'rb') as f:
        global imagedata
        imagedata = pickle.load(f)
        f.close()
    #print(imagedata.kp)
    #print(imagedata.desc)
    for ipoint in imagedata.ipoints:
        print(ipoint)

def captureVideo():
    #cv2.imshow('image',imagedata.image)
    #while(True):
    #    if cv2.waitKey(1) & 0xFF == ord('q'):
    #        break
    #return
    cap = cv2.VideoCapture(0)
    while(True):
        ret, frame = cap.read()
        if ret:
            # Our operations on the frame come here
            cv2.imshow('AR Detection',frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()

def main():
    getData()
    captureVideo()

if __name__ == '__main__':
    main()  