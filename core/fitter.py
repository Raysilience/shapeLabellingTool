#!usr/bin/env python
# coding utf-8
'''
@File       :fitter.py
@Copyright  :CV Group
@Date       :9/8/2021
@Author     :Rui
@Desc       :
'''
import cv2


class Fitter:
    def __init__(self):
        pass

    def fit(self, label, trajectory):
        if label == 'ellipse':
            res = cv2.fitEllipse(trajectory.points)
            return [int(x) for x in [res[0][0], res[0][1], res[1][0], res[1][1], res[2]]]

        # elif label == 'triangle':
