# coding=utf-8
import os
import shutil
import sys
import time

import cv2
from PIL import Image
import numpy as np
import tensorflow as tf

from .nets import model_train as model
from .utils.rpn_msr.proposal_layer import proposal_layer
from .utils.text_connector.detectors import TextDetector

from . import config as cfg

FLAGS = cfg


def resize_image(img,r=1):
    img_size = img.shape
    im_size_min = np.min(img_size[0:2])
    im_size_max = np.max(img_size[0:2])

    im_scale = float(600) / float(im_size_min)
    if np.round(im_scale * im_size_max) > 1200:
        im_scale = float(1200) / float(im_size_max)
    new_h = int(img_size[0] * im_scale)
    new_w = int(img_size[1] * im_scale)

    new_h = new_h if new_h // 16 == 0 else (new_h // 16 + 1) * 16
    new_w = new_w if new_w // 16 == 0 else (new_w // 16 + 1) * 16

    # r=1
    new_w=int(new_w*r)
    new_h=int(new_h*r)
    re_im = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_LINEAR)
    return re_im, (new_h / img_size[0], new_w / img_size[1])

class CacheObject(dict):
    __no_value__ = '<__no_value__>'

    def __getattr__(self, key):
        v = self.get(key, self.__no_value__)
        if v is self.__no_value__:
            self[key] = CacheObject()
            return self[key]
        else:
            return v

    def __setattr__(self, key, value):
        self[key] = value
class Detector:
    def __init__(self):
        self.cache=CacheObject()
        self.graph = tf.Graph()
        with self.graph.as_default():
            self.input_image = tf.placeholder(tf.float32, shape=[None, None, None, 3], name='input_image')
            self.input_im_info = tf.placeholder(tf.float32, shape=[None, 3], name='input_im_info')

            global_step = tf.get_variable('global_step', [], initializer=tf.constant_initializer(0), trainable=False)

            self.bbox_pred, self.cls_pred, self.cls_prob = model.model(self.input_image)

            variable_averages = tf.train.ExponentialMovingAverage(0.997, global_step)
            self.saver = tf.train.Saver(variable_averages.variables_to_restore())
            self.sess = tf.Session(config=tf.ConfigProto(allow_soft_placement=True,
                                                         gpu_options = tf.GPUOptions(per_process_gpu_memory_fraction=0.5)))

            ckpt_state = tf.train.get_checkpoint_state(FLAGS.checkpoint_path)
            model_path = os.path.join(FLAGS.checkpoint_path, os.path.basename(ckpt_state.model_checkpoint_path))
            print('Restore from {}'.format(model_path))
            self.saver.restore(self.sess, model_path)

    def predict_from_file(self, f, scale=1):
        img=cv2.imread(f)
        self.cache['original']=img
        return self.predict(img,scale=scale)
    def predict(self, img ,scale=1):
        r=scale
        os.environ['CUDA_VISIBLE_DEVICES'] = FLAGS.gpu
        img =img[:, :, ::-1]
        img, (rh, rw) = resize_image(img,r=r)
        h, w, c = img.shape
        im_info = np.array([h, w, c]).reshape([1, 3])
        bbox_pred_val, cls_prob_val = self.sess.run([self.bbox_pred, self.cls_prob],
                                                    feed_dict={self.input_image: [img],
                                                               self.input_im_info: im_info})

        textsegs, _ = proposal_layer(cls_prob_val, bbox_pred_val, im_info)
        scores = textsegs[:, 0]
        textsegs = textsegs[:, 1:5]

        textdetector = TextDetector(DETECT_MODE='H')
        boxes = textdetector.detect(textsegs, scores[:, np.newaxis], img.shape[:2])
        boxes=np.array(boxes).astype(np.float)
        boxes[:]/=np.array([rw,rh,rw,rh,rw,rh,rw,rh,1]).astype(np.float)
        boxes=np.array([[box[0],box[1],box[4],box[5]] for box in boxes])
        boxes = np.array(boxes, dtype=np.int)
        # print('before:  (%s, %s) ,now : %s'%(rh,rw,img.shape))
        self.cache['boxes']=boxes
        return boxes, scores
    def show(self, img):
        img=Image.fromarray(np.array(img).astype(np.uint8)[:, :, ::-1])
        img.show()
    def save(self,img,f):
        dir = os.path.dirname(f)
        os.makedirs(dir) if not os.path.exists(dir) else None
        cv2.imencode('.jpg', img)[1].tofile(f)
    def draw_boxes(self,img,boxes):
        for i, box in enumerate(boxes):
            box=np.array([box[0],box[1],box[2],box[1],box[2],box[3],box[0],box[3],0])
            cv2.polylines(img, [box[:8].astype(np.int32).reshape((-1, 1, 2))], True, color=(0, 255, 0),
                          thickness=2)
        return img
    def crop(self,img,box):
        img=Image.fromarray(img).crop(box)
        img=np.array(img)
        return img
if __name__ == '__main__':
    f = 'data/demo/1.jpg'
    P = Detector()
    boxes, scores = P.predict_from_file(f)
    print(boxes)
    img = cv2.imread(f)
    # P.view_boxes(img, boxes)
    im=P.crop(img,boxes[0])
    P.show(im)