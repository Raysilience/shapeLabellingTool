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
