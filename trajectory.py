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
    def __init__(self, points, align_on=True):
        self.points = points
        self._is_align_on = align_on
        self.MAX_ALIGN_RADIAN = math.pi/18
        self.MAX_PARALLEL_SIN = math.sin(math.pi/10 )

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

    def is_parallel(self, begin=True, traj=None):
        """
        determine whether the beginning segment is parallel with the end segment if vec is None, otherwise,
        determine whether the vec is parallel with either beginning or end segment
        :param begin: compare the beginning or the end of points
        :param traj: segment of another trajectory
        :return: True if parallel otherwise False
        """
        if self.get_length() < 4:
            return False
        return MathUtil.calc_sin_angle(self.points[0] - self.points[1], self.points[-2] - self.points[-1]) < self.MAX_PARALLEL_SIN


    def get_length(self):
        return len(self.points)

    def approx_triangle(self):
        if self.get_length() == 4:
            intersection = MathUtil.calc_intersect(self.points[0], self.points[1], self.points[-1], self.points[-2])
            vertices = np.array([intersection, self.points[1], self.points[2]], dtype=np.int32)
        elif self.get_length() == 3:
            vertices = self.points
        else:
            return None

        if self._is_align_on:
            return self._align_shape(vertices)
        else:
            return vertices

    def approx_rectangle(self):
        if self.get_length() == 5:
            intersection = MathUtil.calc_intersect(self.points[0], self.points[1], self.points[-1], self.points[-2])
            vertices = np.array([intersection, self.points[1], self.points[2], self.points[3]], dtype=np.int32)
        elif self.get_length() == 4:
            vertices = self.points
        else:
            return None

        if self._is_align_on:
            return self._align_shape(vertices)
        else:
            return vertices

    def approx_pentagon(self):
        if self.get_length() == 6:
            intersection = MathUtil.calc_intersect(self.points[0], self.points[1], self.points[-1], self.points[-2])
            vertices = np.array([intersection, self.points[1], self.points[2], self.points[3], self.points[4]],
                                dtype=np.int32)
        elif self.get_length() == 5:
            vertices = self.points
        else:
            return None

        vertices = self._approx_regular_polygon(vertices, None)
        if self._is_align_on:
            return self._align_shape(vertices)
        else:
            return vertices

    def approx_hexagon(self):
        if len(self.points) == 7:
            intersection = MathUtil.calc_intersect(self.points[0], self.points[1], self.points[-1], self.points[-2])
            vertices = np.array(
                [intersection, self.points[1], self.points[2], self.points[3], self.points[4], self.points[5]],
                dtype=np.int32)
        elif self.get_length() == 6:
            vertices = self.points
        else:
            return None
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

    def _align_shape(self, vertices):
        center, radius = cv2.minEnclosingCircle(vertices)
        abs_rad = 2 * math.pi
        rad = abs_rad
        for i in range(len(vertices)):
            v0 = vertices[i - 1]
            v1 = vertices[i]
            tmp_rad = self._get_rotation_rad(v0, v1)
            if abs(tmp_rad) < abs_rad:
                abs_rad = abs(tmp_rad)
                rad = tmp_rad

        if abs(rad) > self.MAX_ALIGN_RADIAN:
            return vertices

        vertices_to_origin = vertices - center
        affine_mat = MathUtil.get_affine_matrix(rad)
        tmp_mat = np.dot(vertices_to_origin, affine_mat)
        tmp_mat += center
        tmp_mat = tmp_mat.astype(dtype=np.int32)
        return tmp_mat

    def _get_rotation_rad(self, p0, p1):
        """
        given a straight line, find an optimal radian to align it with either axis
        :param p0: point0 in the form of numpy array
        :param p1: point1 in the form of numpy array
        :return: radian value
        """
        delta_x = p0[0] - p1[0]
        delta_y = p0[1] - p1[1]
        if abs(delta_x) > abs(delta_y):
            rad = MathUtil.calc_radian(p0 - p1, np.array([1, 0]))
            rad = rad if rad < math.pi / 2 else math.pi - rad
            sign = (delta_x < 0 and delta_y < 0) or (delta_x > 0 and delta_y > 0)
        else:
            rad = MathUtil.calc_radian(p0 - p1, np.array([0, 1]))
            rad = rad if rad < math.pi / 2 else math.pi - rad
            sign = (delta_x < 0 and delta_y > 0) or (delta_x > 0 and delta_y < 0)
        sign = 1 if sign else -1
        return sign * rad

