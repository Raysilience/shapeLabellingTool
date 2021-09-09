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

    def regularize(self, label, vertices):
        return vertices