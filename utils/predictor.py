from detect.predict import Detector
from recong.predict import Recongnizer
import cv2
import numpy as np
from PIL import Image
import os,glob,shutil,logging

class BasePredictor:
    def show_img(self,img):
        img = Image.fromarray(np.array(img).astype(np.uint8)[:, :, ::-1])
        img.show()
    def save_img(self, img, f):
        dir = os.path.dirname(f)
        os.makedirs(dir) if not os.path.exists(dir) else None
        cv2.imencode('.jpg', img)[1].tofile(f)
    def predict_from_file(self,f,**kwargs):
        img = cv2.imread(f)
        return self.predict(img, **kwargs)
    def predict(self,img,**kwargs):
        print('***Warning: You need to write a predict() method for your predictor class')
class Predictor(BasePredictor):
    def __init__(self):
        self.D=Detector()
        self.R=Recongnizer()
    def predict_from_file(self,f,show_boxes=False):
        img=cv2.imread(f)
        return self.predict(img,show_boxes=show_boxes)
    def predict(self,img,show_boxes=False,scale=1,detect_out_file=None):
        img=img.copy()
        boxes,scores=self.D.predict(img,scale=scale)
        boxes_img=self.D.draw_boxes(img,boxes)
        detect_out_file='data/output/tmp.jpg' if not detect_out_file else detect_out_file
        self.save(boxes_img,detect_out_file)
        self.show(boxes_img) if show_boxes else None
        boxes2=[]
        for i,box in enumerate(boxes):
            box2={}
            box2['coors']=box
            box2['xmin']=box[0]
            box2['ymin']=box[1]
            box2['xmax']=box[2]
            box2['ymax']=box[3]
            box2['cx']=(box[2]+box[0])//2
            box2['cy']=(box[3]+box[1])//2
            box2['w']=(box[2]-box[0])//2
            box2['h']=(box[3]-box[1])//2
            box2['degree']=0
            im=self.D.crop(img,box)
            box2['text']=self.R.predict(im)
            box2['score']=scores[i]
            boxes2.append(box2)
        return boxes2
    def show(self, img):
        img=Image.fromarray(np.array(img).astype(np.uint8)[:, :, ::-1])
        img.show()
    def save(self,img,f):
        dir=os.path.dirname(f)
        os.makedirs(dir) if not os.path.exists(dir) else None
        cv2.imencode('.jpg',img)[1].tofile(f)