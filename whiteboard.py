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
from classifier import Classifier


class Whiteboard:
    def __init__(self, name='', shape=None) -> None:
        if not name: name = "Whiteboard 1"
        if not shape: shape = (720, 1280, 3)
        self.whiteboard = np.zeros(shape, np.uint8)
        self.whiteboard.fill(255)
        self.whiteboard_name = name
        self.points = []
        self.classifier = Classifier()

    def draw(self):
        cv2.namedWindow(self.whiteboard_name)
        cv2.setMouseCallback(self.whiteboard_name, self._on_mouse_action)
        while 1:
            cv2.imshow(self.whiteboard_name, self.whiteboard)
            if cv2.waitKey(100) == 27:
                break
        cv2.destroyAllWindows()

    def _on_mouse_action(self, event, x, y, flags, param):
        if event == cv2.EVENT_MOUSEMOVE and flags & cv2.EVENT_FLAG_LBUTTON:
            self.points.append((x, y))
            logging.info("x: {}\ty: {}".format(x, y))
            cv2.circle(self.whiteboard, (x, y), 2, (255, 0, 0), 2)
        elif event == cv2.EVENT_LBUTTONUP:
            _points = self.classifier.get_refined_polyline(self.points)
            print(_points)
            self._draw_shape(_points)
            self.points.clear()

    def _draw_shape(self, points):
        if points is not None:
            cv2.polylines(self.whiteboard, [points], True, (0, 255, 0), 2)
            for point in points:
                cv2.circle(self.whiteboard, point, 3, (0, 0, 255), 2)

if __name__ == '__main__':
    LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
    logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)

    whiteboard = Whiteboard()
    whiteboard.draw()
