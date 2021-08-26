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

import MathUtil


def is_convex(vertices):
    """
    check whether all points of a closed graph could form a convex shape
    :param: vertices in the form of numpy array
    :return: boolean
    """
    if len(vertices) < 4:
        return True
    sum_radian = 0
    for i in range(len(vertices)):
        sum_radian += MathUtil.calc_radian(vertices[i - 2] - vertices[i - 1], vertices[i - 1] - vertices[i])

    print(sum_radian)
    return abs(sum_radian - 2 * math.pi) < math.pi / 180