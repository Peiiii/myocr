#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Aug  4 01:01:37 2019
身份证识别
@author: chineseocr
"""
from .image import union_rbox
import re
from utils.tools import Framework
from utils import predictor

class Predictor(predictor.BasePredictor):
    def __init__(self):
        self.P=predictor.Predictor()

    def predict(self, img, *args, **kwargs):
        cls = passport
        res = {}
        for r in [1, 2, 1.5]:
            boxes = self.P.predict(img, scale=r, *args, **kwargs)
            zz = cls(boxes, verbose=False)
            res.update(zz.res)
        return res



def orgnize_boxes(boxes):
    rows = []
    boxes.sort(key=lambda box: int(box['cy']))
    for box in boxes:
        if len(rows) == 0:
            row = [box]
            rows.append(row)
            continue
        last_box = rows[-1][-1]
        if box['cy'] <= last_box['cy'] + int(last_box['h'] * 0.5):
            rows[-1].append(box)
        else:
            row = [box]
            rows.append(row)
    for row in rows:
        row.sort(key=lambda box: int(box['cx']))
    return rows


def find_str_in_box(box, *args):
    txt = box['text'].replace(' ', '')
    txt = txt.replace(' ', '').lower()
    res = []
    for str in args:
        res += re.findall(str, txt)
    if len(res) == 0:
        return None
    return res[0]


class passport:
    """
    护照结构化识别
    """

    def __init__(self, result, verbose=True):
        self.result = union_rbox(result, 0.2)
        self.framework=Framework(result)
        self.rows = orgnize_boxes(self.result)
        if verbose:
            self.print_rows()
        self.N = len(self.result)
        self.res = {}
        self.surname()
        self.given_name()
        self.birth_palce()
        self.birth_date()
        self.sex()
        self.issue_place()
        self.issue_date()
        self.expiry_date()
        self.authority()
        self.type()
        self.country_code()
        self.passport_no()
    def print_rows(self):
        for row in self.rows:
            print(row)
    def surname(self):
        """
        姓
        """
        name = {}
        for i, row in enumerate(self.rows):
            for j, box in enumerate(row):
                if find_str_in_box(box, '姓', '/sur', 'rnam') and i < len(self.rows):
                    b2=self.framework.find_next_downward(box)
                    res=re.findall('[\u4e00-\u9fa5]{1,5}.*[a-zA-Z]$',b2['text'])
                    if len(res):
                        name['姓'] = res[0]
                        self.res.update(name)
                        return

    def given_name(self):
        """
        名
        """
        name = {}
        for i, row in enumerate(self.rows):
            for j, box in enumerate(row):
                if find_str_in_box(box, '名/', '/giv', 'ennam') and i < len(self.rows):
                    b2=self.framework.find_next_downward(box)
                    res=re.findall('[\u4e00-\u9fa5]{1,5}.*[a-zA-Z0-9]$',b2['text'])
                    if len(res):
                        name['名'] = res[0]
                        self.res.update(name)
                        return


    def sex(self):
        """
        名
        """
        name = {}
        for i, row in enumerate(self.rows):
            for j, box in enumerate(row):
                if find_str_in_box(box, '性别', '/se', 'sex') and i < len(self.rows):
                    row2 = self.rows[i + 1]
                    for box in row2:
                        res = find_str_in_box(box, "[\u4e00-\u9fa5]/[a-zA-Z]")
                        if res:
                            name['性别'] = res
                            self.res.update(name)
                            return

    def birth_palce(self):
        """
        名
        """
        name = {}
        for i, row in enumerate(self.rows):
            for j, box in enumerate(row):
                if find_str_in_box(box, '生地点', 'laceofbir') and i < len(self.rows):
                    row2 = self.rows[i + 1]
                    for box2 in row2:
                        res = find_str_in_box(box2, "[\u4e00-\u9fa5]{2,10}/[a-zA-Z]+")
                        if res:
                            name['出生地点'] = res
                            self.res.update(name)
                            return

    def birth_date(self):
        """
        名
        """
        name = {}
        for i, row in enumerate(self.rows):
            for j, box in enumerate(row):
                if find_str_in_box(box, '生日期', '期/d', 'teofbir') and i < len(self.rows):
                    row2 = self.rows[i + 1]
                    for box2 in row2:
                        res = find_str_in_box(box2, "[a-zA-Z0-9]{8,10}")
                        if res:
                            name['出生日期'] = res[:2] + ' ' + res[2:5] + ' ' + res[-4:]
                            self.res.update(name)
                            return

    def issue_place(self):
        """
        名
        """
        name = {}
        for i, row in enumerate(self.rows):
            for j, box in enumerate(row):
                if find_str_in_box(box, '发地点', 'laceofiss') and i < len(self.rows):
                    row2 = self.rows[i + 1]
                    for box2 in row2:
                        res = find_str_in_box(box2, "[\u4e00-\u9fa5]{2,10}/[a-zA-Z]+")
                        if res:
                            name['签发地点'] = res
                            self.res.update(name)
                            return

    def issue_date(self):
        name = {}
        for i, row in enumerate(self.rows):
            for j, box in enumerate(row):
                if find_str_in_box(box, '发日期', 'teofiss') and i < len(self.rows):
                    row2 = self.rows[i + 1]
                    for box2 in row2:
                        res = find_str_in_box(box2, "[0-9]+[a-z]+[0-9]+")
                        if res:
                            name['签发日期'] = res[:2] + ' ' + res[2:5] + ' ' + res[-4:]
                            self.res.update(name)
                            return

    def expiry_date(self):
        name = {}
        for i, row in enumerate(self.rows):
            for j, box in enumerate(row):
                if find_str_in_box(box, '有效期至', '效期至', 'teofexp') and i < len(self.rows):
                    row2 = self.rows[i + 1]
                    for box2 in row2:
                        res = find_str_in_box(box2, "[0-9]+[a-z]+[0-9]+")
                        if res:
                            name['有效期至'] = res[:2] + ' ' + res[2:5] + ' ' + res[-4:]
                            self.res.update(name)
                            return

    def authority(self):
        """
        名
        """
        name = {}
        for i, row in enumerate(self.rows):
            for j, box in enumerate(row):
                if find_str_in_box(box, '签发机关', '发机关', 'authori') and i < len(self.rows):
                    row2 = self.rows[i + 1]
                    if i < len(self.rows) + 1:
                        row2 += self.rows[i + 2]
                    for box2 in row2:
                        res = find_str_in_box(box2, "[\u4e00-\u9fa5]{2,15}")
                        if res:
                            name['签发机关'] = res
                            self.res.update(name)
                            return

    def type(self):
        name = {}
        for i, row in enumerate(self.rows):
            for j, box in enumerate(row):
                if find_str_in_box(box, '类型', '/ty', 'type') and i < len(self.rows):
                    row2 = self.rows[i + 1] + self.rows[i + 2] + self.rows[i + 3]
                    for box2 in row2:
                        res = find_str_in_box(box2, "^[a-zA-Z]$")
                        if res:
                            name['类型'] = res
                            self.res.update(name)
                            return

    def country_code(self):
        name = {}
        for i, row in enumerate(self.rows):
            for j, box in enumerate(row):
                if find_str_in_box(box, '国家码', '家码', 'ountrycod') and i < len(self.rows):
                    row2 = self.rows[i + 1] + self.rows[i + 2] + self.rows[i + 3]
                    for box2 in row2:
                        res = find_str_in_box(box2, "^[a-zA-Z]{2,5}$")
                        if res:
                            name['国家码'] = res
                            self.res.update(name)
                            return

    def passport_no(self):
        name = {}
        for i, row in enumerate(self.rows):
            for j, box in enumerate(row):
                if find_str_in_box(box, '护照号', '/passp', 'portn') and i < len(self.rows):
                    row2 = self.rows[i + 1] + self.rows[i + 2] + self.rows[i + 3]
                    for box2 in row2:
                        res = find_str_in_box(box2, "[a-zA-Z][0-9]{8}")
                        if res:
                            name['护照号'] = res
                            self.res.update(name)
                            return
                        res = find_str_in_box(box2, "[a-zA-Z][0-9]{7,9}")
                        if res:
                            name['护照号'] = '误' + res
                            self.res.update(name)
                            return
