#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Aug  4 01:01:37 2019
身份证识别
@author: chineseocr
"""
from .image import union_rbox
import re, functools,pprint
from utils.tools import Framework
from utils import predictor

class Predictor(predictor.BasePredictor):
    def __init__(self):
        self.P=predictor.Predictor()

    def predict(self, img, *args, print_boxes=False, **kwargs):
        cls = reciept
        res = {}
        # for r in [1,2,1.5]:
        for r in [1]:
            boxes = self.P.predict(img, scale=r, *args, **kwargs)
            zz = cls(boxes, verbose=print_boxes, img_size=(img.shape[0], img.shape[1]))
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


def find_str_in_box(box, *args ,replace_dic=None,to_lower=True):
    txt = box['text'].replace(' ', '')
    txt = txt.replace(' ', '')
    if to_lower:
        txt=txt.lower()
    if replace_dic:
        for k,v in replace_dic.items():
            txt=txt.replace(k,v)
    res = []
    for str in args:
        res += re.findall(str, txt)
    if len(res) == 0:
        return None
    return res[0]



class Entity:
    def __init__(self, boxes, verbose=False,img_size=None):
        # self.result = union_rbox(result, 0.2)
        self.result = boxes
        # self.rows = orgnize_boxes(self.result)
        self.framework = Framework(boxes,img_size=img_size)
        self.rows=self.framework.rows
        if verbose:
            self.framework.print_rows()
        self.N = len(self.result)
        self.cache={}
        self.res = {}
        self.name()
        self.taxpayer_number()
        self.address_and_phone_number()
        self.bank_and_bank_account()

    def bank_and_bank_account(self):
        name = {}
        boxes = self.framework.boxes
        box = self.framework.find_box_by_str(boxes, patterns=['开户行及帐号', '开户行','帐号'])
        if not box: return
        res = find_str_in_box(box, ":.+", replace_dic={'；': ':', '：': ':', ';': ':'})
        if res:
            name['开户行及帐号'] = res.lstrip(':')
            self.res.update(name)
            return
    def address_and_phone_number(self):
        name = {}
        boxes = self.framework.boxes
        box = self.framework.find_box_by_str(boxes, patterns=['地址、电话', '地址','电话'])
        if not box: return
        res = find_str_in_box(box, ":.+", replace_dic={'；': ':', '：': ':', ';': ':'})
        if res:
            name['地址、电话'] = res.lstrip(':')
            self.res.update(name)
            return
    def taxpayer_number(self):
        name = {}
        boxes = self.framework.boxes
        box = self.framework.find_box_by_str(boxes, patterns=['纳税人识别号','识别号','纳税人识'])
        if not box: return
        res = find_str_in_box(box, ":.+",replace_dic={'；':':','：':':',';':':'})
        if res:
            name['纳税人识别号'] = res.lstrip(':')
            self.res.update(name)
            return
    def name(self):
        name = {}
        boxes = self.framework.boxes
        box = self.framework.find_box_by_str(boxes, patterns=['名称:','名称：','名称；', '名称;', '^称','名称'])
        if not box: return
        res = find_str_in_box(box, ":.+",replace_dic={'；':':','：':':',';':':'}) or find_str_in_box(box, "^称.+",replace_dic={'；':':','：':':',';':':'})
        if res:
            name['名称'] = res.lstrip('称').lstrip(':')
            self.res.update(name)
            return




class reciept:
    """
    结构化识别
    """

    def __init__(self, result, verbose=True,img_size=None):
        # self.result = union_rbox(result, 0.2)
        self.result = result
        # self.rows = orgnize_boxes(self.result)
        self.framework = Framework(result,img_size=img_size)
        self.rows=self.framework.rows
        if verbose:
            self.framework.print_rows()
        self.N = len(self.result)
        self.cache={}
        self.res = {}
        self.prepare()
        self.billing_date()
        self.reciept_code()
        self.reciept_number()
        self.check_code()
        self.machine_number()
        self.buyer()
        self.seller()
        self.payee()
        self.drawee()
        self.checker()
        self.total_tax()
        # self.credit_code()
        # self.name()
        # self.type()
        # self.regestered_capital()
        # self.registration_number()
        # self.setup_date()
        # self.legal_man()
        # self.operating_period()
        # self.home_address()
        # self.business_scope()
    def prepare(self):
        self.cache['area1']= self.framework.find_boxes(key=lambda box: self.framework.in_area(box, yr=[0,0.3]))
        self.cache['area2']=self.framework.find_boxes(key=lambda box: self.framework.in_area(box, xr=[0,0.5],yr=[0.2,0.5]))
        self.cache['area3']=self.framework.find_boxes(key=lambda box: self.framework.in_area(box, xr=[0,0.5],yr=[0.5,1]))
        self.cache['area4']=self.framework.find_boxes(key=lambda box: self.framework.in_area(box, xr=[0,1],yr=[0.7,1]))
        self.cache['area5']=self.framework.find_boxes(key=lambda box: self.framework.in_area(box, xr=[0,1],yr=[0.5,0.8]))
        self.cache['area6']=self.framework.find_boxes(key=lambda box: self.framework.in_area(box, xr=[0,1],yr=[0.2,0.8]))
        # Framework(self.cache['area5']).print_rows()
    def total_tax(self):
        name = {}
        boxes = self.cache['area5']
        box = self.framework.find_box_by_str(boxes, patterns=['（小写）','小写'])
        if not box: return
        res = find_str_in_box(box,'[0-9.]+')
        if res:
            name['价税合计'] ='￥'+res
            self.res.update(name)
            return
    def checker(self):
        name = {}
        boxes = self.cache['area4']
        box = self.framework.find_box_by_str(boxes, patterns=['复核'])
        if not box: return
        res = find_str_in_box(box, ":.+", replace_dic={'；': ':', '：': ':', ';': ':'})
        if res:
            name['复核'] = res.lstrip(':')
            self.res.update(name)
            return
    def drawee(self):
        name = {}
        boxes = self.cache['area4']
        box = self.framework.find_box_by_str(boxes, patterns=['开票人', '开票', '票人'])
        if not box: return
        res = find_str_in_box(box, ":.+", replace_dic={'；': ':', '：': ':', ';': ':'})
        if res:
            name['开票人'] = res.lstrip(':')
            self.res.update(name)
            return
    def payee(self):
        name = {}
        boxes = self.cache['area4']
        box = self.framework.find_box_by_str(boxes, patterns=['收款人', '收款', '款人'])
        if not box: return
        res = find_str_in_box(box, ":.+", replace_dic={'；': ':', '：': ':', ';': ':'})
        if res:
            name['收款人'] = res.lstrip(':')
            self.res.update(name)
            return
    def seller(self):
        name={'销售方':Entity(self.cache['area3']).res}
        self.res.update(name)
    def buyer(self):
        name={'购买方':Entity(self.cache['area2']).res}
        self.res.update(name)
    def machine_number(self):
        name = {}
        boxes = self.cache['area1']
        box = self.framework.find_box_by_str(boxes, patterns=['机器编号', '编号'])
        if not box: return
        res = find_str_in_box(box, "[0-9]+")
        if res:
            name['机器编号'] = res
            self.res.update(name)
            return
    def check_code(self):
        name = {}
        boxes = self.cache['area1']
        box = self.framework.find_box_by_str(boxes, patterns=['校验码', '验码'])
        if not box: return
        res = find_str_in_box(box, "[0-9]+")
        if res:
            name['校验码'] = res
            self.res.update(name)
            return
    def reciept_number(self):
        name = {}
        boxes = self.cache['area1']
        box = self.framework.find_box_by_str(boxes, patterns=['发票号码', '号码'])
        if not box: return
        res = find_str_in_box(box, "[0-9]+")
        if res:
            name['发票号码'] = res
            self.res.update(name)
            return
    def reciept_code(self):
        name = {}
        boxes = self.cache['area1']
        box = self.framework.find_box_by_str(boxes, patterns=['发票代码', '代码'])
        if not box: return
        res = find_str_in_box(box, "[0-9]+")
        if res:
            name['发票代码'] = res
            self.res.update(name)
            return
    def billing_date(self):
        name={}
        boxes=self.cache['area1']
        box=self.framework.find_box_by_str(boxes,patterns=['开票日期','票日'])
        if not box:return
        res=find_str_in_box(box,"[0-9]{4}年.{1,3}月.{1,3}日")
        if res:
            name['开票日期'] = res
            self.res.update(name)
            return
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
