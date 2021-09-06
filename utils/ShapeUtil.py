#!usr/bin/env python
# coding utf-8
'''
@File       :ShapeUtil.py
@Copyright  :CV Group
@Date       :8/26/2021
@Author     :Rui
@Desc       :
'''
import math

import cv2
import numpy as np

from utils import MathUtil


def is_convex(vertices):
    """
    check whether all points of a closed graph could form a convex shape
    :param: vertices in the form of numpy array
    :return: boolean
    """
    if len(vertices) < 2:
        return False
    elif len(vertices) < 4:
        return True
    sum_radian = 0
    for i in range(len(vertices)):
        sum_radian += MathUtil.calc_radian(vertices[i - 2] - vertices[i - 1], vertices[i - 1] - vertices[i])

    return abs(sum_radian - 2 * math.pi) < math.pi / 6

def get_rotation_rad(p0, p1):
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


def align_shape(vertices, epsilon):
    """
    align shape against x or y axis
    :param vertices: vertices of shape
    :param epsilon: maximum radian determining align or not
    :return: aligned vertices in the form of numpy array
    """
    center, radius = cv2.minEnclosingCircle(vertices)
    abs_rad = 2 * math.pi
    rad = abs_rad
    for i in range(len(vertices)):
        v0 = vertices[i - 1]
        v1 = vertices[i]
        tmp_rad = get_rotation_rad(v0, v1)
        if abs(tmp_rad) < abs_rad:
            abs_rad = abs(tmp_rad)
            rad = tmp_rad

    if abs(rad) > epsilon:
        return vertices

    vertices_to_origin = vertices - center
    affine_mat = MathUtil.get_affine_matrix(rad)
    tmp_mat = np.dot(vertices_to_origin, affine_mat)
    tmp_mat += center
    tmp_mat = tmp_mat.astype(dtype=np.int32)
    return tmp_mat

def check_parallel(p0, p1, p2, p3, epsilon_rad):
    rad = MathUtil.calc_sin_angle(p0 - p1, p2 - p3)
    return abs(rad) < math.sin(epsilon_rad)

