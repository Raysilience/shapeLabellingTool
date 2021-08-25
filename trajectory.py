#!usr/bin/env python
# coding utf-8
'''
@File       :trajectory.py
@Copyright  :CV Group
@Date       :8/25/2021
@Author     :Rui
@Desc       :
'''
import logging
import math

import cv2
import numpy as np

import MathUtil

class Trajectory:
    def __init__(self, points):
        self.points = points

    def is_closed(self, factor, ord=None):
        """
        check whether the points could synthesis a closed graph
        :param factor which controls the scale of distance between start and end points
        :param ord order of norm
        :return: boolean value indicating closed or not
        """
        if len(self.points) < 3:
            return False
        _, radius = cv2.minEnclosingCircle(self.points)
        return MathUtil.within_ball(self.points[0], self.points[-1], radius * factor, ord)

    def get_length(self):
        return len(self.points)

    def approx_triangle(self):
        if len(self.points) != 4:
            logging.info("number of points is not 4")
            return None
        intersection = MathUtil.calc_intersect(self.points[0], self.points[1], self.points[-1], self.points[-2])
        if intersection is None:
            logging.info("detect parallel lines")
            self.parts.add(tuple(self.points))
            return None
        vertices = np.array([intersection, self.points[1], self.points[2]], dtype=np.int32)
        return vertices

    def approx_rectangle(self):
        if len(self.points) != 5:
            logging.info("number of points is not 5")
            return None
        intersection = MathUtil.calc_intersect(self.points[0], self.points[1], self.points[-1], self.points[-2])
        if intersection is None:
            logging.info("detect parallel lines")
            return None
        vertices = np.array([intersection, self.points[1], self.points[2], self.points[3]], dtype=np.int32)
        return vertices

    def approx_pentagon(self):
        if len(self.points) != 6:
            logging.info("number of points is not 6")
            return None
        intersection = MathUtil.calc_intersect(self.points[0], self.points[1], self.points[-1], self.points[-2])
        if intersection is None:
            logging.info("detect parallel lines")
            return None
        vertices = np.array([intersection, self.points[1], self.points[2], self.points[3], self.points[4]], dtype=np.int32)
        return self._approx_regular_polygon(vertices, None)

    def approx_hexagon(self):
        if len(self.points) != 7:
            logging.info("number of points is not 7")
            return None
        intersection = MathUtil.calc_intersect(self.points[0], self.points[1], self.points[-1], self.points[-2])
        if intersection is None:
            logging.info("detect parallel lines")
            return None

        vertices = np.array([intersection, self.points[1], self.points[2], self.points[3], self.points[4], self.points[5]], dtype=np.int32)
        return self._approx_regular_polygon(vertices, None)


    def _approx_regular_polygon(self, vertices, direction):
        center, radius = cv2.minEnclosingCircle(vertices)
        num_vertices = len(vertices)
        alpha = 2 * math.pi / num_vertices
        rad = MathUtil.calc_radian(vertices[0] - center, np.array([1, 0]))
        reg_shape_at_origin = []

        for v in vertices:
            x, y = MathUtil.polar_to_cartesian(rad, radius)
            reg_shape_at_origin.append([x, -y])
            rad += alpha
        reg_shape_at_origin = np.asarray(reg_shape_at_origin, dtype=np.int32)
        affine_mat = MathUtil.get_affine_matrix(0)
        tmp = np.dot(reg_shape_at_origin, affine_mat)
        tmp = tmp.astype(dtype=np.int32)
        trans = np.array(center, dtype=np.int32)
        return trans + tmp