import cv2
import numpy as np
#author: Shayan Hemmatiyan
# import keras_ocr

# pipeline =keras_ocr.pipeline.Pipeline()


class Generate:
    def __init__(self, img, image_path, download_f, bb, txt):
        # bb [LT, BR]
        self.img = img
        self.image_path=image_path
        self.download_f = download_f
        self.bb = bb
        self.txt = txt

    def fileType(self, fileName):
        fileName = fileName.replace("\\", "/")
        return (str(fileName.split("/")[-1]).split(".")[-1]).lower()

    def fileName(self, filePath):
        filePath = filePath.replace("\\", "/")
        return str(filePath.split("/")[-1]).split(".")[0]
    
    def midpoint(self, x1,x2,y1,y2):
        return (int((x1+x2)/2), int((y1+y2)/2))

    def gen(self):
        new_img_ = self.img.copy()
        font = cv2.FONT_HERSHEY_DUPLEX
        fontScale = 1
        color = (0,0,0)
        start = self.midpoint(self.bb[0][0]+1, self.bb[0][0]+1 , self.bb[0][1]-1, self.bb[1][1]-1)
        end = self.midpoint(self.bb[1][0], self.bb[1][0] , self.bb[0][1], self.bb[1][1])
        tickness = min(max(0,abs(self.bb[1][1]-self.bb[0][1])), int(new_img_.shape[1]))
        start_txt = (self.bb[0][0]+5,start[1]+10)
        mask =np.zeros(new_img_.shape[:2], dtype= "uint8")
        print("p1,p2", (int(start[0]), int(start[1])), (int(end[0]), int(end[1])))
        cv2.line(mask, (int(start[0]), int(start[1])), (int(end[0]), int(end[1])),255, tickness)
        img_generated = cv2.inpaint(new_img_, mask,3, cv2.INPAINT_NS)
        print("bb", self.bb, (int(start[0]), int(start[1])))
        img_generated=cv2.putText(img_generated, self.txt,start_txt,\
             font,fontScale ,color, 1, cv2.LINE_AA)
        print("file", str(self.download_f)+"/gen_"+str(self.fileName(self.image_path) +".png"))
        return img_generated