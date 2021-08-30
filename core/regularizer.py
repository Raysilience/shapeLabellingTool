#!usr/bin/env python
# coding utf-8
'''
@File       :regularizer.py
@Copyright  :CV Group
@Date       :8/30/2021
@Author     :Rui
@Desc       :
'''
from utils import MathUtil


class Regularizer:

    def __init__(self):
        self.type = None
        self.refined_polyline = None
        self.original_sketch = None

    def setData(self, type, refined_polyline, original_sketch=None):
        self.type = type
        self.refined_polyline = refined_polyline
        self.original_sketch = original_sketch

    def regularize(self):
        if self.type == 'triangle':
            pass
        elif self.type == 'rectangle':
            pass
        elif self.type == 'pentagon':
            pass
        elif self.type == 'hexagon':
            pass
        elif self.type == 'ellipse':
            pass

    def _template_match_triangle(self):
        rads = self.calc_inner_angle()
        assert (len(rads) == 3)


    def calc_inner_angle(self):
        if self.refined_polyline is None or len(self.refined_polyline) < 3:
            return []
        res = []
        for i in range(len(self.refined_polyline)):
            res.append(MathUtil.calc_radian(self.refined_polyline[i - 2] - self.refined_polyline[i - 1],
                                            self.refined_polyline[i - 1] - self.refined_polyline[i]))
        return res
