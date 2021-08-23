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
        self.MIN_BALL_RADIUS = 20
        self.MIN_DISTINGUISH_ANGLE = math.cos(math.pi / 6)
        self.NUM_OF_CONSECUTIVE_POINTS = 10

    def check_convexity_and_turning_points(self, points):
        if len(points) < self.NUM_OF_CONSECUTIVE_POINTS:
            logging.info("u'd better increase sampling frequency or draw longer lines")
            return False, None
        turning_points = []
        clockwise = None
        for i in range(0, len(points) - self.NUM_OF_CONSECUTIVE_POINTS):
            if i == 0:
                turning_points.append(points[i])
                continue
            vec1 = np.asarray(points[i]) - np.asarray(points[i + self.NUM_OF_CONSECUTIVE_POINTS//2 - 1])
            vec2 = np.asarray(points[i + self.NUM_OF_CONSECUTIVE_POINTS//2 - 1]) - np.asarray(points[i + self.NUM_OF_CONSECUTIVE_POINTS - 1])
            vec_c = np.cross(vec1, vec2)
            cos_theta = MathUtil.calc_cos_angle(vec1, vec2)
            if cos_theta < self.MIN_DISTINGUISH_ANGLE :
                if not MathUtil.within_ball(turning_points[-1], points[i + self.NUM_OF_CONSECUTIVE_POINTS//2 - 1], self.MIN_BALL_RADIUS, 1):
                    turning_points.append(points[i + self.NUM_OF_CONSECUTIVE_POINTS//2 - 1])
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
        if not MathUtil.within_ball(turning_points[-1], points[-1], self.MIN_BALL_RADIUS, 1):
            turning_points.append(points[-1])
        return True, turning_points
