#!usr/bin/env python
# coding utf-8
"""
@File       :test.py
@Copyright  :CV Group
@Date       :8/23/2021
@Author     :Rui
@Desc       :
"""

import numpy as np


def calc_cos_angle(vec1, vec2):
    mod1 = np.linalg.norm(vec1)
    mod2 = np.linalg.norm(vec2)
    return np.dot(vec1, vec2) / (mod1 * mod2) if mod1 * mod2 != 0 else 0


def calc_sin_angle(vec1, vec2):
    mod1 = np.linalg.norm(vec1)
    mod2 = np.linalg.norm(vec2)
    vec_c = np.cross(vec1, vec2)
    return np.linalg.norm(vec_c) / (mod1 * mod2) if mod1 * mod2 != 0 else 0


def within_ball(point1, point2, epsilon, ord=None):
    vec = np.asarray(point1) - np.asarray(point2)
    dis = np.linalg.norm(vec, ord)
    return dis < epsilon


def calc_intersect(p0, p1, p2, p3):
    # line 0
    a0 = p0[1] - p1[1]
    b0 = p1[0] - p0[0]
    c0 = p0[1] * p1[0] - p0[0] * p1[1]

    # line 1
    a1 = p2[1] - p3[1]
    b1 = p3[0] - p2[0]
    c1 = p2[1] * p3[0] - p2[0] * p3[1]

    if a0 * b1 == a1 * b0:
        return None
    else:
        denom = a0 * b1 - a1 * b0

    x = (c1 * b0 - c0 * b1) / denom
    y = (c0 * a1 - c1 * a0) / denom
    return (x, y)
