
import os
import json
import time

import numpy as np
from PIL import Image
import cv2

from . import config as cfg

from .crnn.keys import alphabetChinese, alphabetEnglish
from .crnn.network_torch import CRNN


class Recongnizer:
    def __init__(self):
        alphabet = alphabetChinese
        ocrModel =cfg.ocrModelTorchLstm
        nclass = len(alphabet) + 1
        self.model=CRNN(32, 1, nclass, 256, leakyRelu=False, lstmFlag=cfg.LSTMFLAG, GPU=cfg.GPU, alphabet=alphabet)
        self.model.load_weights(ocrModel)
    def predict_from_file(self,f):
        img=cv2.imread(f)
        return self.predict(img)
    def predict(self,img):
        img=Image.fromarray(img).convert('L')
        y=self.model.predict(img)
        return y

if __name__ == '__main__':
    P=Recongnizer()
    f = 'data/single_line/1.jpg'
    y=P.predict_from_file(f)
    print(y)