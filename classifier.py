import logging
import math

import numpy as np

import MathUtil


class Classifier:
    def __init__(self):
        # self.CONVEX_TOLERANCE
        pass

    def check_convexity_and_turning_points(self, points):
        if len(points) < 3:
            logging.info("length less than 3")
            return False, None
        turning_points = []
        clockwise = None
        for i in range(0, len(points) - 2, 2):
            vec1 = np.asarray(points[i]) - np.asarray(points[i + 1])
            vec2 = np.asarray(points[i + 1]) - np.asarray(points[i + 2])
            vec_c = np.cross(vec1, vec2)
            cos_theta = MathUtil.calc_cos_angle(vec1, vec2)
            print(cos_theta)
            if (cos_theta < math.cos(math.pi/6)):
                turning_points.append(points[i+1])
                is_clockwise = None
                if vec_c > 0:
                    is_clockwise = False
                if vec_c < 0:
                    is_clockwise = True
                if clockwise is None and is_clockwise is not None:
                    clockwise = is_clockwise
                    continue
                if clockwise is not None and is_clockwise is not None:
                    if clockwise^is_clockwise:
                        return False, None

        return True, turning_points
