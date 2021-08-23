#!usr/bin/env python
# coding utf-8
"""
@File       :test.py
@Copyright  :CV Group
@Date       :8/23/2021
@Author     :Rui
@Desc       :
"""

import logging
import math

import numpy as np

import MathUtil


class Classifier:
    def __init__(self):
        # self.CONVEX_TOLERANCE
        pass

    def check_convexity_and_turning_points(self, points):
        if len(points) < 5:
            logging.info("length less than 5")
            return False, None
        turning_points = []
        clockwise = None
        for i in range(0, len(points) - 10):
            if i == 0:
                turning_points.append(points[i])
                continue
            vec1 = np.asarray(points[i]) - np.asarray(points[i + 4])
            vec2 = np.asarray(points[i + 4]) - np.asarray(points[i + 9])
            vec_c = np.cross(vec1, vec2)
            cos_theta = MathUtil.calc_cos_angle(vec1, vec2)
            if cos_theta < math.cos(math.pi / 6):
                if not MathUtil.within_ball(turning_points[-1], points[i+2], 15, 1):
                    turning_points.append(points[i+4])
                is_clockwise = None
                if vec_c > 0:
                    is_clockwise = False
                if vec_c < 0:
                    is_clockwise = True
                if clockwise is None and is_clockwise is not None:
                    clockwise = is_clockwise
                    continue
                if clockwise is not None and is_clockwise is not None:
                    if clockwise ^ is_clockwise:
                        return False, None
        if not MathUtil.within_ball(turning_points[-1], points[-1], 15, 1):
            turning_points.append(points[-1])
        return True, turning_points
