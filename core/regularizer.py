#!usr/bin/env python
# coding utf-8
'''
@File       :regularizer.py
@Copyright  :CV Group
@Date       :8/30/2021
@Author     :Rui
@Desc       :
'''
import math

import cv2

from utils import MathUtil


class Regularizer:

    def __init__(self):
        self.MAX_EQUALITERAL_RELAXATION_RAD = math.pi / 12

    def regularize(self, label, vertices):
        sub_label = ''

        if label == 'ellipse':
            res = cv2.fitEllipse(vertices)
            x, y = res[0]
            axis_w, axis_h = res[1]
            angle = res[2]
            if abs(axis_h - axis_w) < 15:
                avg = (axis_h + axis_w) / 2
                axis_w, axis_h = avg, avg
                sub_label = 'circle'
            return sub_label, [int(x) for x in [x, y, axis_w, axis_h, angle]]
        elif label == 'triangle':
            radians = []
            equaliteral = True
            for i in range(len(vertices)):
                rad = MathUtil.calc_radian(vertices[i] - vertices[i - 1], vertices[i] - vertices[i - 2])
                if abs(rad - math.pi/3) > self.MAX_EQUALITERAL_RELAXATION_RAD:
                    equaliteral = False
            if equaliteral:
                sub_label = 'equaliteral triangle'
            else:
                pass

