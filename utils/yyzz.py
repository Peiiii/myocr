#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Aug  4 01:01:37 2019
身份证识别
@author: chineseocr
"""
from .image import union_rbox
import re, functools
from utils import predictor

class Predictor(predictor.BasePredictor):
    def __init__(self):
        self.P=predictor.Predictor()
    def predict(self,img, *args, **kwargs):
        cls = yyzz
        res = {}
        # for r in [1,2,1.5]:
        for r in [1.25, 1.75]:
            boxes = self.P.predict(img, scale=r, *args, **kwargs)
            zz = cls(boxes, verbose=False)
            jyfw = res.get('经营范围', '')
            jyfw_new = zz.res.get('经营范围', '')
            if len(jyfw_new) > len(jyfw):
                jyfw = jyfw_new
            res.update(zz.res)
            res['经营范围'] = jyfw
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


class Framework():
    def __init__(self, boxes):
        self.rows = self.orgnize_boxes(boxes)
        self.boxes = []
        k=0
        for i, row in enumerate(self.rows):
            for j, box in enumerate(row):
                box['pos'] = (i, j)
                box['index']=k
                self.rows[i][j]=box
                self.boxes.append(box)
                k+=1
        self.cache={}
    def find_next_n(self, box, n):
        m, n = box['pos']
        boxes = []
        num = 0
        end = False
        for i, row in enumerate(self.rows[m:]):
            if end:
                break
            for j, box in enumerate(row[n:]):
                boxes.append(box)
                num += 1
                if num == n + 1:
                    end = True
                    break
        boxes = boxes[1:]
        return boxes

    def find_pos(self, box):
        cx, cy = box['cx'], box['cy']
        for b in self.boxes:
            if b['cx'] == cx and b['cy'] == cy:
                return b['pos']

    def find_down(self, box):
        m, n = box['pos']
        if m >= len(self.rows):
            return None
        cands = self.rows[m + 1]
        cands = sorted(cands, key=lambda b: (b['cx'] - box['cx']) ** 2 + (b['cy'] - box['cy']) ** 2)
        return cands[0]

    def connect_vertical_downward(self, box):
        box['pos'] = self.find_pos(box)
        m, n = box['pos']
        boxset = []

        def is_vertically_adjacent(b1, b2):
            ro = 0.2  # 横向超出占行宽的最大比重
            rv = 3  # 纵向距离占行高的最大比重
            if b2['cx'] > b1['xmax'] or b2['cx'] < b1['xmin']: return False
            if b2['cy'] < b2['cy'] or (b2['cy'] - b1['cy']) > b1['h'] * rv: return False

            ofl = b1['xmin'] - b2['xmin'] if b2['xmin'] < b1['xmin'] else 0
            ofr = b2['xmax'] - b1['xmax'] if b2['xmax'] > b1['xmax'] else 0
            off = ofl + ofr
            if off > ro * b1['w']: return False
            return True

        for row in self.rows[m:]:
            for b in row[n:]:
                if len(boxset) == 0:
                    boxset.append(b)
                    continue
                if is_vertically_adjacent(boxset[-1], b): boxset.append(b)
        self.cache['boxset']=boxset
        return boxset

    def orgnize_boxes(self,boxes):
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
    def print_rows(self):
        for row in self.rows:
            print(row)



class yyzz:
    """
    护照结构化识别
    """

    def __init__(self, result, verbose=True):
        self.result = union_rbox(result, 0.2)
        # self.rows = orgnize_boxes(self.result)
        self.framework = Framework(result)
        self.rows=self.framework.rows
        if verbose:
            self.framework.print_rows()
        self.N = len(self.result)
        self.res = {}
        self.credit_code()
        self.name()
        self.type()
        self.regestered_capital()
        self.registration_number()
        self.setup_date()
        self.legal_man()
        self.operating_period()
        self.home_address()
        self.business_scope()

    def credit_code(self):
        name = {}
        for i, row in enumerate(self.rows):
            for j, box in enumerate(row):
                if find_str_in_box(box, '社会信用代码', '信用代码', '信用代') and i < len(self.rows):
                    row2 = self.gather_rows([i, i + 7])
                    for box in row2:
                        res = find_str_in_box(box, "[0-9]{15,20}[a-zA-Z]$")
                        if res:
                            name['统一社会信用代码'] = res
                            self.res.update(name)
                            return

    def name(self):
        name = {}
        for i, row in enumerate(self.rows):
            for j, box in enumerate(row):
                if find_str_in_box(box, '名称', '^称$', '^称', '[\u4e00-\u9fa5]{2,30}公司') and i < len(self.rows):
                    row2 = self.gather_rows([i, i + 7])
                    for box in row2:
                        res = find_str_in_box(box, "[\u4e00-\u9fa5()（）]{2,30}公司")
                        if res:
                            res = res.strip('名').strip('称')
                            name['名称'] = res
                            self.res.update(name)
                            return

    def type(self):
        name = {}
        for i, row in enumerate(self.rows):
            for j, box in enumerate(row):
                if find_str_in_box(box, '类型', '^型$', '^型') and i < len(self.rows):
                    row2 = self.gather_rows([i, i + 2])
                    for box in row2:
                        res = find_str_in_box(box, "型[\u4e00-\u9fa5]{2,30}公司.*")
                        if res:
                            res = res.strip('型')
                            name['类型'] = res
                            self.res.update(name)
                            return

    def regestered_capital(self):
        name = {}
        for i, row in enumerate(self.rows):
            for j, box in enumerate(row):
                if find_str_in_box(box, '注册资本', '册资', '资本$') and i < len(self.rows):
                    row2 = self.gather_rows([i, i + 1])
                    # res = self.find_str_boxes("[美]?[元]?[0-9\.]+[十百千万亿]*[元]?",row2)
                    res = self.find_str_boxes("资本.*", row2)
                    if len(res):
                        name['注册资本'] = res[0].lstrip('资本')
                        self.res.update(name)
                        return
    def registration_number(self):
        name = {}
        for i, row in enumerate(self.rows):
            for j, box in enumerate(row):
                if find_str_in_box(box, '注册号', '册号', '^号') and i < len(self.rows):
                    row2 = self.framework.find_next_n(box, 2) + [box]
                    res = find_str_in_box(box, '[0-9]{13,15}')
                    if res:
                        name['注册号'] = res
                        self.res.update(name)
                        return
    def setup_date(self):
        name = {}
        for i, row in enumerate(self.rows):
            for j, box in enumerate(row):
                if find_str_in_box(box, '成立日期', '成立', '日期') and i < len(self.rows):
                    row2 = self.gather_rows([i, i + 1])
                    res = self.find_str_boxes("[0-9]{4}年[0-9]{1,2}月[0-9]{1,2}日", row2)
                    if len(res):
                        name['成立日期'] = res[0]
                        self.res.update(name)
                        return

    def legal_man(self):
        name = {}
        for i, row in enumerate(self.rows):
            for j, box in enumerate(row):
                if find_str_in_box(box, '法定代表人', '代表人', '定代表', '法定') and i < len(self.rows):
                    row2 = self.framework.find_next_n(box, 1) + [box]
                    # print('find , rows:',row2)
                    res = self.find_str_boxes("代表人[\u4e00-\u9fa5]{2,5}$", row2)
                    if len(res):
                        name['法定代表人'] = res[0].strip('代表人')
                        self.res.update(name)
                        return



    def operating_period(self):
        name = {}
        for i, row in enumerate(self.rows):
            for j, box in enumerate(row):
                if find_str_in_box(box, '营业期限', '业期', '期限$') and i < len(self.rows):
                    row2 = self.framework.find_next_n(box, 1) + [box]
                    res = self.find_str_boxes("期限.*", row2)
                    if len(res):
                        name['营业期限'] = res[0].lstrip('期限')
                        self.res.update(name)
                        return

    def home_address(self):
        name = {}
        for i, row in enumerate(self.rows):
            for j, box in enumerate(row):
                if find_str_in_box(box, '住所', '^所') and i < len(self.rows):
                    row2 = self.framework.find_next_n(box, 2) + [box]
                    res = self.find_str_boxes("所.*", row2)
                    if len(res):
                        name['住所'] = res[0].lstrip('所')
                        self.res.update(name)
                        return

    def business_scope(self):
        name = {}
        for i, row in enumerate(self.rows):
            for j, box in enumerate(row):
                if find_str_in_box(box, '经营范围', '营范', '范围', '^围') and i < len(self.rows):
                    text = self.extend_text_downward(box)
                    res = re.findall('围.*', text)
                    if len(res):
                        name['经营范围'] = res[0].lstrip('围')
                        self.res.update(name)
                        return

    def extend_text_downward(self, box):
        boxes = self.framework.connect_vertical_downward(box)
        text = ''.join([b['text'] for b in boxes])
        return text

    def gather_rows(self, interval):
        start, end = interval
        end = len(self.rows) if end is None else min(len(self.rows), end)
        rows = functools.reduce(lambda a, b: a + b, self.rows[start:end])
        return rows

    def find_str_boxes(self, str, boxes):
        boxes2 = []
        for box in boxes:
            res = re.findall(str, box['text'])
            if len(res) != 0:
                boxes2.append(res[0])
        return boxes2
