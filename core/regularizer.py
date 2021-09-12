#!usr/bin/env python
# coding utf-8
'''
@File       :regularizer.py
@Copyright  :CV Group
@Date       :8/30/2021
@Author     :Rui
@Desc       :
'''
import logging
import math

import cv2
import numpy as np

from utils import MathUtil, ShapeUtil


class Regularizer:

    def __init__(self):
        self.MAX_EQUILATERAL_RAD_RELAXATION = math.pi / 12
        self.MAX_PARALLEL_RAD_RELAXATION = math.pi / 8
        self.MAX_VERTICAL_RAD_RELAXATION = math.pi / 12
        self.MAX_DIAG_DIFF_FACTOR = 0.2

    def regularize(self, label, vertices):
        sub_label = ''
        vertices = np.asarray(vertices)
        descriptor = []
        if label == 'ellipse':
            res = cv2.fitEllipse(vertices)
            x, y = res[0]
            axis_w, axis_h = res[1]
            angle = res[2]
            if abs(axis_h - axis_w) < 15:
                avg = (axis_h + axis_w) / 2
                axis_w, axis_h = avg, avg
                sub_label = 'circle'
            return sub_label, [int(x) for x in [x, y, axis_w, axis_h, angle]]
        elif label == 'triangle':
            radians = []
            equilateral = True
            for i in range(len(vertices)):
                rad = MathUtil.calc_radian(vertices[i] - vertices[i - 1], vertices[i] - vertices[i - 2])
                if abs(rad - math.pi/3) > self.MAX_EQUILATERAL_RAD_RELAXATION:
                    equilateral = False
            if equilateral:
                sub_label = 'equilateral triangle'
                center, radius = cv2.minEnclosingCircle(vertices)
                direct0 = MathUtil.calc_uniform_vec(center - vertices[0])
                length = MathUtil.calc_eucleadian_dist(center, vertices[0])
                aff_max = MathUtil.get_affine_matrix(math.pi * 2 / 3)
                direct1 = np.dot(aff_max, direct0)
                direct2 = np.dot(aff_max, direct1)
                vertices[1] = ShapeUtil.translate(center, direct1, length)
                vertices[2] = ShapeUtil.translate(center, direct2, length)
                vertices[2] = center

            else:
                pass
        elif label == 'quadrangle':
            if ShapeUtil.check_parallel(vertices[0], vertices[1], vertices[2], vertices[3], self.MAX_PARALLEL_RAD_RELAXATION) and \
                    ShapeUtil.check_parallel(vertices[0], vertices[3], vertices[1], vertices[2], self.MAX_PARALLEL_RAD_RELAXATION):
                sub_label = 'parallelogram'
                diag02 = MathUtil.calc_eucleadian_dist(vertices[0], vertices[2])
                diag13 = MathUtil.calc_eucleadian_dist(vertices[1], vertices[3])
                if diag02 < diag13:
                    diag02, diag13 = diag13, diag02
                    logging.debug('vertices: {}'.format(vertices))
                    tmp = [vertices[i] for i in [3, 0, 1, 2]]
                    vertices = np.asarray(tmp)

                cross_point = np.asarray(MathUtil.calc_intersect(vertices[0], vertices[2], vertices[1], vertices[3]))
                mid_point = (vertices[0] + vertices[2]) / 2
                direct1 = MathUtil.calc_uniform_vec(cross_point - vertices[1])
                direct3 = -direct1
                length = diag13 / 2

                if diag02 - diag13 < self.MAX_DIAG_DIFF_FACTOR * diag02:
                    sub_label = 'rectangle'
                    length = diag02 / 2
                    if ShapeUtil.check_diag_vertical(vertices[0], vertices[1], vertices[2], vertices[3], self.MAX_VERTICAL_RAD_RELAXATION):
                        sub_label = 'square'
                        direct0 = MathUtil.calc_uniform_vec(cross_point - vertices[0])
                        aff_max = MathUtil.get_affine_matrix(math.pi / 2)
                        direct1 = np.dot(aff_max, direct0)
                        direct3 = -direct1
                else:
                    if ShapeUtil.check_diag_vertical(vertices[0], vertices[1], vertices[2], vertices[3], self.MAX_VERTICAL_RAD_RELAXATION):
                        sub_label = 'diamond'
                        direct0 = MathUtil.calc_uniform_vec(cross_point - vertices[0])
                        aff_max = MathUtil.get_affine_matrix(math.pi / 2)
                        direct1 = np.dot(aff_max, direct0)
                        direct3 = -direct1

                vertices[1] = ShapeUtil.translate(mid_point, direct1, length)
                vertices[3] = ShapeUtil.translate(mid_point, direct3, length)
                vertices = ShapeUtil.align_shape(vertices, self.MAX_PARALLEL_RAD_RELAXATION)

        return sub_label, vertices.tolist()


