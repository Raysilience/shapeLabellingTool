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
    def __init__(self):
        self.MIN_BALL_RADIUS = 40
        self.MIN_DISTINGUISH_ANGLE = math.cos(math.pi / 6)
        self.NUM_OF_CONSECUTIVE_POINTS = 15
        self.MAX_CLOSED_FACTOR = 0.4
        self.ALIGN_SHAPE = True
        self.parts = set()
        self.LABELS = ['unknown', 'circle', 'line', 'triangle', 'rectangle', 'pentagon', 'hexagon',  'ellipse', 'form_extension']

    def detect(self, points):
        """
        detect whether a sequence of points represents a geometric shape
        :param points: a sequence of points sampled in a specific sampling rate
        :return: vector of points if any, otherwise, None
        """
        pts = None
        _points = self._find_turning_points(points)
        trajectory = Trajectory(_points, self.ALIGN_SHAPE)

        # one touch drawing
        if trajectory.is_closed(self.MAX_CLOSED_FACTOR):
            if ShapeUtil.is_convex(_points[:-1]):
                pts = self._approx_polygon(trajectory)

        # multi touches drawing
        else:
            if ShapeUtil.is_convex(_points):
                pts = self._match_trajectory(trajectory)
                # pts could not form a polygon add it to part
                if pts is None:
                    self.parts.add(trajectory)

        if pts is None:
            label = self.LABELS[0]
        else:
            label = self.LABELS[len(pts)]
        return label, pts


    # Todo: optimize matching process with bisection
    def _match_trajectory(self, trajectory):
        """
        match two trajectory. if they can concatenate into a closed convex shape return it otherwise store it
        in the parts
        :param trajectory: current trajectory to be matched
        :return: points of a new shape if it meets requirements otherwise None
        """
        pts = None
        logging.debug("number of parts: {}\n".format(len(self.parts)))
        for part in list(self.parts):
            traj, cnt_match = trajectory.match(part)
            logging.debug("number of matched points: {}\n".format(cnt_match))

            if traj is not None and ShapeUtil.is_convex(traj.points):
                if cnt_match == 1:
                    self.parts.add(traj)
                elif cnt_match == 2:
                    pts = ShapeUtil.align_shape(traj.points, traj.MAX_ALIGN_RADIAN)
                    self.parts.remove(part)
        return pts

    def _find_turning_points(self, points):
        """
        check graph convexity and find robust turning points in the graph
        :param points: sampling points
        :return: boolean, points
        """
        turning_points = []
        last_cos_theta = 1
        if len(points) < self.NUM_OF_CONSECUTIVE_POINTS:
            logging.info("u'd better increase sampling frequency or draw longer lines")
            return turning_points
        for i in range(0, len(points) - self.NUM_OF_CONSECUTIVE_POINTS):
            if i == 0:
                turning_points.append(points[i])
                continue
            vec1 = np.asarray(points[i]) - np.asarray(points[i + self.NUM_OF_CONSECUTIVE_POINTS // 2 - 1])
            vec2 = np.asarray(points[i + self.NUM_OF_CONSECUTIVE_POINTS // 2 - 1]) - np.asarray(
                points[i + self.NUM_OF_CONSECUTIVE_POINTS - 1])
            cos_theta = MathUtil.calc_cos_angle(vec1, vec2)
            if cos_theta < self.MIN_DISTINGUISH_ANGLE:
                within_ball = MathUtil.within_ball(turning_points[-1], points[i + self.NUM_OF_CONSECUTIVE_POINTS // 2 - 1], self.MIN_BALL_RADIUS, 1)
                if not within_ball:
                    turning_points.append(points[i + self.NUM_OF_CONSECUTIVE_POINTS // 2 - 1])
                    last_cos_theta = cos_theta
                else:
                    if cos_theta < last_cos_theta:
                        turning_points.pop()
                        turning_points.append(points[i + self.NUM_OF_CONSECUTIVE_POINTS // 2 - 1])
                        last_cos_theta = cos_theta
        turning_points.append(points[-1])
        turning_points = np.asarray(turning_points)
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
