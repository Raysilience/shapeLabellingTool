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

    def detect(self, points):
        """
        detect whether a sequence of points represents a geometric shape
        :param points: a sequence of points sampled in a specific sampling rate
        :return: vector of points if any, otherwise, None
        """
        is_convex, _points = self._check_convexity_and_turning_points(points)
        if is_convex:
            trajectory = Trajectory(_points, self.ALIGN_SHAPE)
            if trajectory.is_closed(self.MAX_CLOSED_FACTOR):
                return self._get_refined_polyline(trajectory)
            else:
                self.parts.add(trajectory)
        return None

    def _check_convexity_and_turning_points(self, points):
        """
        check graph convexity and find robust turning points in the graph
        :param points: sampling points
        :return: boolean, points
        """
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

    def _get_refined_polyline(self, trajectory):
        """
        determine which kind of shape the trajectory represents and fine tune the shape
        :param trajectory: of the shape
        :return: the vertices of polyline
        """
        logging.info("detect {} points".format(trajectory.get_length()))
        if trajectory.get_length() < 4:
            pass
        elif trajectory.get_length() == 4:
            return trajectory.approx_triangle()

        elif trajectory.get_length() == 5:
            if trajectory.is_parallel():
                trajectory.points = trajectory.points[1:-1]
                return trajectory.approx_triangle()
            else:
                return trajectory.approx_rectangle()

        elif trajectory.get_length() == 6:
            if trajectory.is_parallel():
                trajectory.points = trajectory.points[1:-1]
                return trajectory.approx_rectangle()
            else:
                return trajectory.approx_pentagon()

        elif trajectory.get_length() == 7:
            if trajectory.is_parallel():
                trajectory.points = trajectory.points[1:-1]
                return trajectory.approx_pentagon()
            else:
                return trajectory.approx_hexagon()

        elif trajectory.get_length() == 8:
            if trajectory.is_parallel():
                trajectory.points = trajectory.points[1:-1]
                return trajectory.approx_hexagon()
        else:
            logging.info("reach the maximum of turning points, fail to detect")
        return None
