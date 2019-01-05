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
        global database
        database = pickle.load(f)
        f.close()
    global compass
    compass = cv2.imread("compass4.jpg", cv2.IMREAD_UNCHANGED)
    compass = image_resize(compass, height=40)
       

def captureVideo():
    # Initialize feature matching objects and convert pickled data to original format as needed
    sift = cv2.xfeatures2d.SIFT_create()
    bf = cv2.BFMatcher()
    # Start video capture and loop for continuous frame capturing
    cap = cv2.VideoCapture(0)
    imgChangeCount=0
    ImgIndex=0
    while(True):
        ret, frame = cap.read()
        if ret: 
            kp2, frame_desc = sift.detectAndCompute(frame,None)
            if(kp2 is None or frame_desc is None):
                continue
             # Find image with best matches in database
            bestMatches = 0
            imagedata=None
            good_matches = []
            for entry in database:
                kp1 = getCVKeypoints(entry.kp)
                matches = bf.knnMatch(entry.desc,frame_desc, k=2)
                if(len(matches)==0):
                    continue
                # Apply ratio test to filter bad matches out
                good_matches = filterMatches(matches)
                if(len(good_matches)>bestMatches):
                    imagedata=entry
                    bestMatches=len(good_matches)
            # If enough matches
            if len(good_matches)>MIN_MATCH_COUNT:
                # Calculate Homography between keypoints in the original image and the matching keypoints in frame
                src_pts = np.float32([ kp1[m.queryIdx].pt for m in good_matches ]).reshape(-1,1,2)
                dst_pts = np.float32([ kp2[m.trainIdx].pt for m in good_matches ]).reshape(-1,1,2)
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
                if(closestIPoint is not None):
                    # Circle on interest point itself
                    frame = cv2.circle(frame,(closestIPoint[0],closestIPoint[1]),10,(0,255,0),-1)
                    # If interest point has multiple associated images check if it's time to change image
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

                if not int(image_center[1]-compass.shape[0]/2) < 0 and not int(image_center[1]+compass.shape[0]/2) > frame.shape[0] and not image_center[0]-compass.shape[1] < 0 and not image_center[0] > frame.shape[1]:
                    
                    frame[int(image_center[1]-compass.shape[0]/2):int(image_center[1]+compass.shape[0]/2), image_center[0]-compass.shape[1]:image_center[0], :] = \
                    frame[int(image_center[1]-compass.shape[0]/2):int(image_center[1]+compass.shape[0]/2), image_center[0]-compass.shape[1]:image_center[0], :] * (1 - compass[:, :, 3:] / np.iinfo(compass.dtype).max) + \
                    compass[:, :, :3] * (compass[:, :, 3:] / np.iinfo(compass.dtype).max)
            else:
                print("Not enough matches are found - %d/%d" % (len(good_matches),MIN_MATCH_COUNT))
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

def image_resize(image, width = None, height = None, inter = cv2.INTER_AREA):
    # initialize the dimensions of the image to be resized and
    # grab the image size
    dim = None
    (h, w) = image.shape[:2]
    # if both the width and height are None, then return the
    # original image
    if width is None and height is None:
        return image
    # check to see if the width is None
    if width is None:
        # calculate the ratio of the height and construct the
        # dimensions
        r = height / float(h)
        dim = (int(w * r), height)
    # otherwise, the height is None
    else:
        # calculate the ratio of the width and construct the
        # dimensions
        r = width / float(w)
        dim = (width, int(h * r))

    # resize the image
    resized = cv2.resize(image, dim, interpolation = inter)
    # return the resized image
    return resized

def main():
    getData()
    captureVideo()

if __name__ == '__main__':
    main()  
