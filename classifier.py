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
from trajectory import Trajectory


class Classifier:
    def __init__(self):
        self.MIN_BALL_RADIUS = 40
        self.MIN_DISTINGUISH_ANGLE = math.cos(math.pi / 6)
        self.NUM_OF_CONSECUTIVE_POINTS = 10
        self.MAX_CLOSED_FACTOR = 0.4
        self.ALIGN_SHAPE = True
        self.parts = set()

    def _check_convexity_and_turning_points(self, points):
        if len(points) < self.NUM_OF_CONSECUTIVE_POINTS:
            logging.info("u'd better increase sampling frequency or draw longer lines")
            return False, None
        turning_points = []
        clockwise = None
        for i in range(0, len(points) - self.NUM_OF_CONSECUTIVE_POINTS):
            if i == 0:
                turning_points.append(points[i])
                continue
            vec1 = np.asarray(points[i]) - np.asarray(points[i + self.NUM_OF_CONSECUTIVE_POINTS // 2 - 1])
            vec2 = np.asarray(points[i + self.NUM_OF_CONSECUTIVE_POINTS // 2 - 1]) - np.asarray(
                points[i + self.NUM_OF_CONSECUTIVE_POINTS - 1])
            vec_c = np.cross(vec1, vec2)
            cos_theta = MathUtil.calc_cos_angle(vec1, vec2)
            if cos_theta < self.MIN_DISTINGUISH_ANGLE:
                if not MathUtil.within_ball(turning_points[-1], points[i + self.NUM_OF_CONSECUTIVE_POINTS // 2 - 1],
                                            self.MIN_BALL_RADIUS, 1):
                    turning_points.append(points[i + self.NUM_OF_CONSECUTIVE_POINTS // 2 - 1])
            if cos_theta < math.cos(math.pi / 5):
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
        turning_points.append(points[-1])
        turning_points = np.asarray(turning_points)
        return True, turning_points

    def get_refined_polyline(self, points):
        flag, _points = self._check_convexity_and_turning_points(points)
        traj = Trajectory(_points, self.ALIGN_SHAPE)
        if flag:
            logging.info("detect {} points".format(traj.get_length()))
            if traj.get_length() == 2:
                self.parts.add(traj)
            elif traj.get_length() == 3:
                self.parts.add(traj)
            elif traj.get_length() == 4:
                if traj.is_closed(self.MAX_CLOSED_FACTOR):
                    return traj.approx_triangle()
                else:
                    self.parts.add(traj)
            elif traj.get_length() == 5:
                if traj.is_closed(self.MAX_CLOSED_FACTOR):
                    return traj.approx_rectangle()
                else:
                    self.parts.add(traj)
            elif traj.get_length() == 6:
                if traj.is_closed(self.MAX_CLOSED_FACTOR):
                    return traj.approx_pentagon()
                else:
                    self.parts.add(traj)
            elif traj.get_length() == 7:
                if traj.is_closed(self.MAX_CLOSED_FACTOR):
                    return traj.approx_hexagon()
                else:
                    self.parts.add(traj)
            elif len(_points) > 7:
                logging.info("reach the maximum of turning points, fail to detect")
        return None