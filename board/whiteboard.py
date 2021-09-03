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


class Whiteboard:
    def __init__(self, name='', shape=None, mode='interactive') -> None:
        if not name: name = "Whiteboard 1"
        if not shape: shape = (720, 1280, 3)
        self.whiteboard = np.zeros(shape, np.uint8)
        self.whiteboard.fill(255)
        self.whiteboard_name = name
        self.points = []
        self.classifier = Classifier()
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
                label, pts = self.classifier.detect(self.points)
                logging.info("\nlabel: {}\ndescriptor: \n{}".format(label, pts))
                self._draw_shape(label, pts)
                self.points.clear()

    def _draw_shape(self, label, points, line_color=(0, 255, 0), point_color=(0, 0, 255)):
        if points is not None:
            if label == 'circle':
                cv2.circle(self.whiteboard, points[0], points[1], line_color, 2)
            else:
                cv2.polylines(self.whiteboard, [points], True, line_color, 2)
                for point in points:
                    cv2.circle(self.whiteboard, point, 3, point_color, 2)
