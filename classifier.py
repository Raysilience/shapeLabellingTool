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

import cv2
import numpy as np

import MathUtil


class Classifier:
    def __init__(self):
        self.MIN_BALL_RADIUS = 20
        self.MIN_DISTINGUISH_ANGLE = math.cos(math.pi / 6)
        self.MIN_CLOSED_DISTANCE = 50
        self.NUM_OF_CONSECUTIVE_POINTS = 10
        self.parts = set()

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
            vec1 = np.asarray(points[i]) - np.asarray(points[i + self.NUM_OF_CONSECUTIVE_POINTS // 2 - 1])
            vec2 = np.asarray(points[i + self.NUM_OF_CONSECUTIVE_POINTS // 2 - 1]) - np.asarray(
                points[i + self.NUM_OF_CONSECUTIVE_POINTS - 1])
            vec_c = np.cross(vec1, vec2)
            cos_theta = MathUtil.calc_cos_angle(vec1, vec2)
            if cos_theta < self.MIN_DISTINGUISH_ANGLE:
                if not MathUtil.within_ball(turning_points[-1], points[i + self.NUM_OF_CONSECUTIVE_POINTS // 2 - 1],
                                            self.MIN_BALL_RADIUS, 1):
                    turning_points.append(points[i + self.NUM_OF_CONSECUTIVE_POINTS // 2 - 1])
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
        return True, turning_points

    def get_refined_polyline(self, points):
        flag, _points = self.check_convexity_and_turning_points(points)
        if flag:
            logging.info("detect {} points".format(len(_points)))
            if len(_points) == 2:
                self.parts.add(tuple(_points))
            elif len(_points) == 3:
                self.parts.add(tuple(_points))
            elif len(_points) == 4:
                if MathUtil.within_ball(_points[0], _points[-1], self.MIN_CLOSED_DISTANCE, 1):
                    return self._approxTriangle(_points)
                else:
                    self.parts.add(tuple(_points))
            elif len(_points) == 5:
                if MathUtil.within_ball(_points[0], _points[-1], self.MIN_CLOSED_DISTANCE, 1):
                    return self._approxRectangle(_points)
                else:
                    self.parts.add(tuple(_points))
            elif len(_points) == 6:
                if MathUtil.within_ball(_points[0], _points[-1], self.MIN_CLOSED_DISTANCE, 1):
                    return self._approxPentagon(_points)
                else:
                    self.parts.add(tuple(_points))
            elif len(_points) == 7:
                if MathUtil.within_ball(_points[0], _points[-1], self.MIN_CLOSED_DISTANCE, 1):
                    return self._approxHexagon(_points)
                else:
                    self.parts.add(tuple(_points))
            elif len(_points) > 7:
                logging.info("reach the maximum of turning points, fail to detect")
        return None

    def _approxTriangle(self, points):
        if len(points) != 4:
            logging.info("number of points is not 4")
            return None
        intersection = MathUtil.calc_intersect(points[0], points[1], points[-1], points[-2])
        if intersection is None:
            logging.info("detect parallel lines")
            self.parts.add(tuple(points))
            return None
        vertices = np.array([intersection, points[1], points[2]], dtype=np.int32)
        return vertices

    def _approxRectangle(self, points):
        if len(points) != 5:
            logging.info("number of points is not 5")
            return None
        intersection = MathUtil.calc_intersect(points[0], points[1], points[-1], points[-2])
        if intersection is None:
            logging.info("detect parallel lines")
            self.parts.add(tuple(points))
            return None
        vertices = np.array([intersection, points[1], points[2], points[3]], dtype=np.int32)
        return vertices

    def _approxPentagon(self, points):
        if len(points) != 6:
            logging.info("number of points is not 6")
            return None
        intersection = MathUtil.calc_intersect(points[0], points[1], points[-1], points[-2])
        if intersection is None:
            logging.info("detect parallel lines")
            self.parts.add(tuple(points))
            return None
        vertices = np.array([intersection, points[1], points[2], points[3], points[4]], dtype=np.int32)
        return vertices

    def _approxHexagon(self, points):
        if len(points) != 7:
            logging.info("number of points is not 7")
            return None
        intersection = MathUtil.calc_intersect(points[0], points[1], points[-1], points[-2])
        if intersection is None:
            logging.info("detect parallel lines")
            self.parts.add(tuple(points))
            return None

        vertices = np.array([intersection, points[1], points[2], points[3], points[4], points[5]], dtype=np.int32)
        return vertices



    def _approx_regular_polygon(self, points, start, direction):
        center, radius = cv2.minEnclosingCircle(points)
        num_vertices = len(points)
        alpha = 2 * math.pi / num_vertices
        angle = 0
        reg_shape_at_origin = []
        for p in points:
            reg_shape_at_origin.append(MathUtil.polar_to_cartesian(angle, radius))
            angle += alpha


        return reg_shape_at_origin