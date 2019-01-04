import cv2
import sys
import math
import numpy as np
import pickle
from tkinter.filedialog import askopenfilename
import tkinter
from ImageData import ImageData



MIN_MATCH_COUNT = 45
IMAGE_CHANGE_COUNT = 20
def getData():
    root = tkinter.Tk()
    root.withdraw()
    filename = askopenfilename(title = "Select Preparation Data")
    with open(filename, 'rb') as f:
        global imagedata
        imagedata = pickle.load(f)
        f.close()
        for ipoint in imagedata.ipoints:
            imagedata.image = cv2.rectangle(imagedata.image,tuple(ipoint.pt2),tuple(ipoint.pt1),(0,0,255))

def captureVideo():
    # Initialize feature matching objects and convert pickled data to original format as needed
    sift = cv2.xfeatures2d.SIFT_create()
    bf = cv2.BFMatcher()
    kp1 = getCVKeypoints(imagedata.kp)
    # Start video capture and loop for continuous frame capturing
    cap = cv2.VideoCapture(0)
    imgChangeCount=0
    ImgIndex=0
    while(True):
        ret, frame = cap.read()
        if ret:  
            # Match natural features of original image with captured video frame  
            kp2, frame_desc = sift.detectAndCompute(frame,None)
            if(kp2 is None or frame_desc is None):
                continue
            matches = bf.knnMatch(imagedata.desc,frame_desc, k=2)
            if(len(matches)==0):
                continue
            # Apply ratio test to filter bad matches out
            good = filterMatches(matches)
            # If enough matches
            if len(good)>MIN_MATCH_COUNT:
                # Calculate Homography between keypoints in the original image and the matching keypoints in frame
                src_pts = np.float32([ kp1[m.queryIdx].pt for m in good ]).reshape(-1,1,2)
                dst_pts = np.float32([ kp2[m.trainIdx].pt for m in good ]).reshape(-1,1,2)
                M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC,5.0)
                # Check if Homography matrix was found
                if(M is None):
                    continue
                if(len(imagedata.image.shape)==3):
                    h,w,channels = imagedata.image.shape
                else:
                    h,w = imagedata.image.shape 
                if(len(frame.shape)==3):
                    fh,fw,fchannels = frame.shape
                else:
                    fh,fw = frame.shape 
                # get centers of interest points in original image
                centers = buildCentersList(imagedata.ipoints)
                # append center of original image
                centers.append([w/2,h/2])
                # Calculate coordinates of the corners and center of the map based on homography matrix
                pts = np.float32([centers]).reshape(-1,1,2)
                dst = cv2.perspectiveTransform(pts,M)
                # Draw yellow circle in center of image
                image_center = np.int32(dst[-1])[0]
                frame = cv2.circle(frame,(image_center[0],image_center[1]),10,(0,255,255),-1)
                # Check for nearest interest point
                minDistance=sys.maxsize
                index=-1
                closestIPoint = None
                for idx in range(0,len(centers)-1):
                    tempDistance=calcEuclidean(image_center,centers[idx])
                    if minDistance > tempDistance:
                        minDistance = tempDistance
                        closestIPoint = np.int32(dst[idx])[0]
                        index = idx
                # Nearest interest point processing
                if(closestIPoint is not None):
                    frame = cv2.circle(frame,(closestIPoint[0],closestIPoint[1]),10,(0,255,0),-1)
                    if(imgChangeCount>=IMAGE_CHANGE_COUNT):
                        imgChangeCount=0
                        ImgIndex=updateImgIndex(imagedata.ipoints[idx].imagesArray,ImgIndex)
                    # Rectangle for picture and interest point name
                    cv2.rectangle(frame,(fw-201,fh-190),(fw-1,fh-1),(170,170,170),cv2.FILLED)
                    # Connect interest point in image to the rectangle displaying info
                    cv2.arrowedLine(frame,(closestIPoint[0],closestIPoint[1]), (fw-201,fh-190), (170,170,170), 5)
                    # Resizing image of nearest interest point
                    resized_image = cv2.resize(imagedata.ipoints[idx].imagesArray[ImgIndex], (200, 150))
                    # Blending the interest point image with the frame, positioned in the corner
                    overlay_image_alpha(frame,resized_image[:,:,0:3],(fw-201,fh-151),resized_image[:,:,2]/255.0)
                    # Drawing name of interest point on screen
                    font = cv2.FONT_HERSHEY_PLAIN
                    cv2.putText(frame,imagedata.ipoints[idx].InterestPointName,(fw-201,fh-170), font, 1,(1,1,1),1,cv2.LINE_AA)
                    #frame = cv2.rectangle(frame,(fw-1,fh-1),(fw-250,fh-150),(0,255,0))
            else:
                print("Not enough matches are found - %d/%d" % (len(good),MIN_MATCH_COUNT))
            cv2.imshow('AR Detection',frame)
            imgChangeCount+=1
            if cv2.waitKey(1) & 0xFF == ord('q'):
                        break
    cap.release()
    cv2.destroyAllWindows()

# https://stackoverflow.com/questions/14063070/overlay-a-smaller-image-on-a-larger-image-python-opencv
def overlay_image_alpha(img, img_overlay, pos, alpha_mask):
    """Overlay img_overlay on top of img at the position specified by
    pos and blend using alpha_mask.

    Alpha mask must contain values within the range [0, 1] and be the
    same size as img_overlay.
    """
    x, y = pos

    # Image ranges
    y1, y2 = max(0, y), min(img.shape[0], y + img_overlay.shape[0])
    x1, x2 = max(0, x), min(img.shape[1], x + img_overlay.shape[1])

    # Overlay ranges
    y1o, y2o = max(0, -y), min(img_overlay.shape[0], img.shape[0] - y)
    x1o, x2o = max(0, -x), min(img_overlay.shape[1], img.shape[1] - x)

    # Exit if nothing to do
    if y1 >= y2 or x1 >= x2 or y1o >= y2o or x1o >= x2o:
        return

    channels = img.shape[2]

    alpha = alpha_mask[y1o:y2o, x1o:x2o]
    alpha_inv = 1.0 - alpha
    for c in range(channels):
        img[y1:y2, x1:x2, c] = (alpha * img_overlay[y1o:y2o, x1o:x2o, c] +
                                alpha_inv * img[y1:y2, x1:x2, c])

def updateImgIndex(arrayImages,currentIndex):
    # Move index to next image
    if(currentIndex<len(arrayImages)-1):
        return currentIndex+1
    # Loop back around
    else:
        return 0

def getCVKeypoints(kps):
    keypoints = []
    for point in kps:
      keypoints.append(cv2.KeyPoint(x=point[0][0],y=point[0][1],_size=point[1], _angle=point[2], 
                            _response=point[3], _octave=point[4], _class_id=point[5]))
    return keypoints

def filterMatches(matches):
    good = []
    if(len(matches[0])<2):
        return good
    for m,n in matches:
        if m.distance < 0.75*n.distance:
            good.append(m)
    return good

def buildCentersList(ips):
    centers = []
    for ip in ips:
        centers.append(ip.center)
    return centers

def printPickle(imagedata):
    for ipoint in imagedata.ipoints:
        print(ipoint)

def calcEuclidean(a,b):
    return math.sqrt((a[0]-b[0])**2 + (a[1]-b[1])**2)

def main():
    getData()
    captureVideo()

if __name__ == '__main__':
    main()  