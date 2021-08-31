#!usr/bin/env python
# coding utf-8
'''
@File       :trajectory.py
@Copyright  :CV Group
@Date       :8/25/2021
@Author     :Rui
@Desc       :
'''
import math

import cv2
import numpy as np

from utils import MathUtil, ShapeUtil


class Trajectory:
    def __init__(self, points, align_on=True):
        self.points = points
        self._is_align_on = align_on
        self.MAX_ALIGN_RADIAN = math.pi / 18
        self.MAX_PARALLEL_RADIAN = math.pi / 10
        self.MAX_PARALLEL_SIN = math.sin(self.MAX_PARALLEL_RADIAN)
        self.MAX_MATCH_DISTANCE = 20

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

    def is_parallel(self):
        """
        determine whether the beginning segment is parallel with the end segment if vec is None, otherwise,
        determine whether the vec is parallel with either beginning or end segment
        :param begin: compare the beginning or the end of points
        :param traj: segment of another trajectory
        :return: True if parallel otherwise False
        """
        if self.get_length() < 4:
            return False
        else:
            return MathUtil.calc_sin_angle(self.points[0] - self.points[1],
                                           self.points[-2] - self.points[-1]) < self.MAX_PARALLEL_SIN

    def match(self, trajectory):
        """
        determine whether two trajectory matches
        :param trajectory:
        :return: trajectory if two trajectories combine into a new one
        """
        num_matching_points = 0
        opt = [0, -1]
        # status[0] is state of param trajectory; status[1] is state of the host trajectory;
        status = [1, 1]
        for i in opt:
            for j in opt:
                if i == status[0] or j == status[1]:
                    continue
                if MathUtil.within_ball(trajectory.points[i], self.points[j], self.MAX_MATCH_DISTANCE):
                    status[0] = i
                    status[1] = j
                    num_matching_points += 1


        if num_matching_points == 1:
            rad = MathUtil.calc_radian(trajectory.points[status[0]] - trajectory.points[3 * status[0] + 1],
                                       self.points[status[1]] - self.points[3 * status[1] + 1])
            parallel = abs(rad - math.pi) < self.MAX_PARALLEL_RADIAN
            return self.concat_points(status[0], status[1], parallel, trajectory.points, self.points), 1

        elif num_matching_points == 2:
            rad0 = MathUtil.calc_radian(trajectory.points[status[0]] - trajectory.points[3 * status[0] + 1],
                                        self.points[status[1]] - self.points[3 * status[1] + 1])
            parallel0 = abs(rad0 - math.pi) < self.MAX_PARALLEL_RADIAN
            rad1 = MathUtil.calc_radian(trajectory.points[-status[0] - 1] - trajectory.points[-3 * status[0] - 2],
                                        self.points[-status[1]-1] - self.points[-3 * status[1] - 2])
            parallel1 = abs(rad1 - math.pi) < self.MAX_PARALLEL_RADIAN
            if parallel0:
                trajectory.points = np.delete(trajectory.points, status[0], axis=0)
            if parallel1:
                trajectory.points = np.delete(trajectory.points, -status[0]-1, axis=0)

            if status[0]^status[1] == 0:
                self.points = self.points[::-1]

            ans = np.append(trajectory.points, self.points[1:-1], axis=0)
            if len(ans) > 1:
                return Trajectory(ans), 2
        return None, 0



    def concat_points(self, status0, status1, parallel, pts0, pts1):
        val = 1 if parallel else 0
        if status0 == 0 and status1 == 0:
            return Trajectory(np.append(pts0[:0:-1], pts1[val:], axis=0))
        elif status0 == 0 and status1 == -1:
            return Trajectory(np.append(pts1[:-1], pts0[val:], axis=0))
        elif status0 == -1 and status1 == 0:
            return Trajectory(np.append(pts0[:-1], pts1[val:], axis=0))
        elif status0 == -1 and status1 == -1:
            return Trajectory(np.append(pts0[:len(pts0) - val], pts1[:0:-1], axis=0))

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
            return ShapeUtil.align_shape(vertices, self.MAX_ALIGN_RADIAN)
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
            return ShapeUtil.align_shape(vertices, self.MAX_ALIGN_RADIAN)
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

        # vertices = self._approx_regular_polygon(vertices, None)
        if self._is_align_on:
            return ShapeUtil.align_shape(vertices, self.MAX_ALIGN_RADIAN)
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
        # return self._approx_regular_polygon(vertices, None)
        return vertices


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
