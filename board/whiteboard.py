#!usr/bin/env python
# coding utf-8
"""
@File       :test.py
@Copyright  :CV Group
@Date       :8/23/2021
@Author     :Rui
@Desc       :
"""

import cv2
import numpy as np
import logging
from core.classifier import Classifier
from math import atan2, cos, sin, sqrt, pi


class Whiteboard:
    def __init__(self, name='', shape=None, mode='interactive') -> None:
        if not name: name = "Whiteboard 1"
        if not shape: shape = (720, 1280, 3)
        self.whiteboard = np.zeros(shape, np.uint8)
        self.whiteboard.fill(255)
        self.whiteboard_name = name
        self.points = []
        self.mode = mode

    def set_points(self, points):
        self.points = points

    def draw(self):
        cv2.namedWindow(self.whiteboard_name)
        if self.mode == 'interactive':
            cv2.setMouseCallback(self.whiteboard_name, self._on_mouse_action)
            while 1:
                cv2.imshow(self.whiteboard_name, self.whiteboard)
                if cv2.waitKey(100) == 27:
                    break
        else:
            self._draw_shape('', self.points, line_color=(255, 0, 255))
            label, pts = self.classifier.detect(self.points)
            logging.info("\nlabel: {}\ndescriptor: \n{}".format(label, pts))
            self._draw_shape(label, pts)
            cv2.imshow(self.whiteboard_name, self.whiteboard)
            cv2.waitKey()
        cv2.destroyAllWindows()

    def _on_mouse_action(self, event, x, y, flags, param):
        if event == cv2.EVENT_MOUSEMOVE and flags & cv2.EVENT_FLAG_LBUTTON:
            self.points.append((x, y))
            logging.debug("x: {}\ty: {}".format(x, y))
            cv2.circle(self.whiteboard, (x, y), 2, (255, 0, 0), 2)
        elif event == cv2.EVENT_LBUTTONUP:
            if self.points is not None:
                # label, pts = self.classifier.detect(self.points)
                # logging.info("\nlabel: {}\ndescriptor: \n{}".format(label, pts))
                # self._draw_shape(label, pts)

                self.points = np.asarray(self.points)
                self.points = cv2.approxPolyDP(self.points, 10, False).astype(np.int32)
                self.points = np.resize(self.points, (len(self.points), 2))
                self._draw_shape('', self.points)

                self.points = self.points.tolist()
                self.getOrientation(self.points, self.whiteboard)



                self.points.clear()

    def _draw_shape(self, label, points, line_color=(0, 255, 0), point_color=(0, 0, 255)):
        if points is not None:
            if label == 'circle':
                cv2.circle(self.whiteboard, points[0], points[1], line_color, 2)
            else:
                # cv2.polylines(self.whiteboard, [points], True, line_color, 2)
                for point in points:
                    cv2.circle(self.whiteboard, point, 3, point_color, 2)

    def drawAxis(self, img, p_, q_, colour, scale):
        p = list(p_)
        q = list(q_)

        angle = atan2(p[1] - q[1], p[0] - q[0])  # angle in radians
        hypotenuse = sqrt((p[1] - q[1]) * (p[1] - q[1]) + (p[0] - q[0]) * (p[0] - q[0]))
        # Here we lengthen the arrow by a factor of scale
        q[0] = p[0] - scale * hypotenuse * cos(angle)
        q[1] = p[1] - scale * hypotenuse * sin(angle)
        cv2.line(img, (int(p[0]), int(p[1])), (int(q[0]), int(q[1])), colour, 1, cv2.LINE_AA)
        # create the arrow hooks
        p[0] = q[0] + 9 * cos(angle + pi / 4)
        p[1] = q[1] + 9 * sin(angle + pi / 4)
        cv2.line(img, (int(p[0]), int(p[1])), (int(q[0]), int(q[1])), colour, 1, cv2.LINE_AA)
        p[0] = q[0] + 9 * cos(angle - pi / 4)
        p[1] = q[1] + 9 * sin(angle - pi / 4)
        cv2.line(img, (int(p[0]), int(p[1])), (int(q[0]), int(q[1])), colour, 1, cv2.LINE_AA)


    def getOrientation(self, pts, img):
        sz = len(pts)
        data_pts = np.empty((sz, 2), dtype=np.float64)

        for i in range(data_pts.shape[0]):
            data_pts[i, 0] = pts[i][0]
            data_pts[i, 1] = pts[i][1]
        # Perform PCA analysis
        mean = np.empty((0))
        mean, eigenvectors, eigenvalues = cv2.PCACompute2(data_pts, mean)
        # Store the center of the object
        cntr = (int(mean[0, 0]), int(mean[0, 1]))

        cv2.circle(img, cntr, 3, (255, 0, 255), 2)
        p1 = (
        cntr[0] + 0.02 * eigenvectors[0, 0] * eigenvalues[0, 0], cntr[1] + 0.02 * eigenvectors[0, 1] * eigenvalues[0, 0])
        p2 = (
        cntr[0] - 0.02 * eigenvectors[1, 0] * eigenvalues[1, 0], cntr[1] - 0.02 * eigenvectors[1, 1] * eigenvalues[1, 0])
        self.drawAxis(img, cntr, p1, (0, 255, 0), 1)
        self.drawAxis(img, cntr, p2, (255, 255, 0), 5)
        angle = atan2(eigenvectors[0, 1], eigenvectors[0, 0])  # orientation in radians

        return angle
