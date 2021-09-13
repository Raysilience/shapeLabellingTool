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

from utils import MathUtil, ShapeUtil
from core.trajectory import Trajectory


class Classifier:
    def __init__(self, config):
        self.MIN_BALL_RADIUS = config.getint('params', 'MIN_BALL_RADIUS')
        self.MIN_DISTINGUISH_ANGLE = math.cos(config.getint('params', 'MIN_DISTINGUISH_ANGLE') * math.pi / 180)
        self.NUM_OF_CONSECUTIVE_POINTS = config.getint('params', 'NUM_OF_CONSECUTIVE_POINTS')
        self.MODEL_PATH = config.get('model', 'MODEL_PATH')

        self.LABELS = ['unknown', 'form_extension', 'line', 'ellipse', 'triangle', 'quadrangle', 'pentagon', 'hexagon']
        self.SUB_LABELS = ['circle']
        self.NUM_TO_SUB_LABEL = {3: 'triangle', 4: 'quadrangle', 5: 'pentagon', 6: 'hexagon'}
        self.peri = 0
        self.area = 0

    def detect_shape(self, points):
        """
        detect whether a sequence of points represents a geometric shape
        :param points: a sequence of points sampled in a specific sampling rate
        :return: label and vector points if any; otherwise, None
        """



    def detect_cnn(self, trajectory):

        pass

    def detect_tradition(self, trajectory):
        """
        use tradition feature engineering method to detect shape
        :param trajectory: a group of sampling points in the form of Trajectory object
        :return: a tuple of label in str, descriptor in list
        """
        label = "unknown"
        descriptor = []

        pts = None
        _points = self.find_turning_points(trajectory.points)
        thinness = self.peri * self.peri / (self.area + 1e-9)
        logging.debug("\nperi: {}\narea: {}:\nthinness: {}".format(self.peri, self.area,
                                                                   self.peri * self.peri / (self.area + 1e-9)))

        # detect circle
        if 12.56 < thinness < 13.85:
            return self.LABELS[3], trajectory.points

        trajectory = Trajectory(_points)

        # one touch drawing
        if ShapeUtil.is_convex(_points[:-1]):
            pts = self._approx_polygon(trajectory)

        if pts is None:
            label = self.LABELS[0]
        else:
            refined_area, _ = MathUtil.calc_polygon_area_perimeter(pts)
            area_diff_ratio = abs(refined_area - self.area) / self.area
            logging.debug("\narea diff ratio: {}".format(area_diff_ratio))
            if area_diff_ratio < 0.3:
                label = self.NUM_TO_SUB_LABEL[len(pts)]
                descriptor = pts.tolist()
        return label, descriptor


    def find_turning_points(self, points):
        """
        check graph convexity and find robust turning points in the graph
        :param points: sampling points
        :return: boolean, points
        """
        turning_points = []
        last_cos_theta = 1
        self.peri = 0
        self.area = 0
        if len(points) < self.NUM_OF_CONSECUTIVE_POINTS:
            logging.info("u'd better increase sampling frequency or draw longer lines")
            return turning_points
        for i in range(len(points)):
            self.peri += np.linalg.norm(np.asarray(points[i - 1]) - np.asarray(points[i]))
            self.area += points[i - 1][0] * points[i][1] - points[i][0] * points[i - 1][1]
            if i == 0:
                turning_points.append(points[i])
                continue

            if i < len(points) - self.NUM_OF_CONSECUTIVE_POINTS:
                vec1 = np.asarray(points[i]) - np.asarray(points[i + self.NUM_OF_CONSECUTIVE_POINTS // 2 - 1])
                vec2 = np.asarray(points[i + self.NUM_OF_CONSECUTIVE_POINTS // 2 - 1]) - np.asarray(
                    points[i + self.NUM_OF_CONSECUTIVE_POINTS - 1])
                cos_theta = MathUtil.calc_cos_angle(vec1, vec2)
                if cos_theta < self.MIN_DISTINGUISH_ANGLE:
                    within_ball = MathUtil.within_ball(turning_points[-1],
                                                       points[i + self.NUM_OF_CONSECUTIVE_POINTS // 2 - 1],
                                                       self.MIN_BALL_RADIUS, 1)
                    if not within_ball:
                        turning_points.append(points[i + self.NUM_OF_CONSECUTIVE_POINTS // 2 - 1])
                        last_cos_theta = cos_theta
                    else:
                        if cos_theta < last_cos_theta:
                            turning_points.pop()
                            turning_points.append(points[i + self.NUM_OF_CONSECUTIVE_POINTS // 2 - 1])
                            last_cos_theta = cos_theta

        if not MathUtil.within_ball(turning_points[-1],points[-1], self.MIN_BALL_RADIUS, 1):
            turning_points.append(points[-1])
        turning_points = np.asarray(turning_points)

        self.area = 0.5 * abs(self.area)

        return turning_points

    def _approx_polygon(self, trajectory):
        """
        determine which kind of shape the trajectory represents and fine tune the shape
        :param trajectory: of the shape
        :return: the vertices of polyline
        """
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

    def detect_customized_shape(self, trajectory):
        logging.debug("into customize")
        label = ''
        descriptor = []
        if trajectory.get_length() == 2:
            if ShapeUtil.check_parallel(trajectory.points[0], trajectory.points[1], np.array([0, 0]), np.array([0, 1]),
                                        trajectory.MAX_PARALLEL_RADIAN) or \
                    ShapeUtil.check_parallel(trajectory.points[0], trajectory.points[1], np.array([0, 0]),
                                             np.array([1, 0]), trajectory.MAX_PARALLEL_RADIAN):
                label = 'line'
                descriptor = trajectory.points.tolist()
        elif trajectory.get_length() == 4:
            if trajectory.is_parallel():
                if ShapeUtil.check_parallel(trajectory.points[0], trajectory.points[1], np.array([0, 0]),
                                            np.array([0, 1]), trajectory.MAX_PARALLEL_RADIAN) or \
                        ShapeUtil.check_parallel(trajectory.points[0], trajectory.points[1], np.array([0, 0]),
                                                 np.array([1, 0]), trajectory.MAX_PARALLEL_RADIAN):
                    if abs(trajectory.points[0][0] - trajectory.points[-1][0]) < 20 or abs(trajectory.points[0][1] - trajectory.points[-1][1]) < 20:
                        label =  'form_extension'
                        descriptor = trajectory.points.tolist()

        return label, descriptor
