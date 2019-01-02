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
  

def printPickle(imagedata):
    print(imagedata.kp)
    print(imagedata.desc)
    for ipoint in imagedata.ipoints:
        print(ipoint)

def captureVideo():
    #cv2.imshow('imagex',imagedata.image)
    #while(True):
    #    if cv2.waitKey(1) & 0xFF == ord('q'):
    #        break
    #return
    orb = cv2.ORB_create()
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    kp1 = getCVKeypoints(imagedata.kp)
    cap = cv2.VideoCapture(0)
    while(True):
        ret, frame = cap.read()
        if ret:
            # Our operations on the frame come here    
            kp2, frame_desc = orb.detectAndCompute(frame,None)
            matches = bf.match(imagedata.desc,frame_desc)
            matches = sorted(matches, key = lambda x:x.distance)
            # Do Homeography here
            frame = cv2.drawMatches(imagedata.image,kp1,frame,kp2,matches[:10],0, flags=2)
            cv2.imshow('AR Detection',frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()

def getCVKeypoints(kps):
    keypoints = []
    for point in kps:
      keypoints.append(cv2.KeyPoint(x=point[0][0],y=point[0][1],_size=point[1], _angle=point[2], 
                            _response=point[3], _octave=point[4], _class_id=point[5]))
    return keypoints

def main():
    getData()
    captureVideo()

if __name__ == '__main__':
    main()  