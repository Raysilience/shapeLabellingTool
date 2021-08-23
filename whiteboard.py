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
        cv2.setMouseCallback(self.whiteboard_name, self._OnMouseAction)
        while 1:
            cv2.imshow(self.whiteboard_name, self.whiteboard)
            if cv2.waitKey(100) == 27:
                break
        cv2.destroyAllWindows()

    def _OnMouseAction(self, event, x, y, flags, param):
        if event == cv2.EVENT_MOUSEMOVE and flags & cv2.EVENT_FLAG_LBUTTON:
            self.points.append((x, y))
            logging.info("x: {}\ty: {}".format(x, y))
            cv2.circle(self.whiteboard, (x, y), 2, (255, 0, 0), 2)
        elif event == cv2.EVENT_LBUTTONUP:
            if len(self.points) > 0:
                flag, _points = self.classifier.check_convexity_and_turning_points(self.points)
                if flag:
                    for point in _points:
                        cv2.circle(self.whiteboard, point, 3, (0, 0, 255), 2)
                print("flag: {}, _points: {}".format(flag, _points))
            self.points.clear()


if __name__ == '__main__':
    LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
    logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)

    whiteboard = Whiteboard()
    whiteboard.draw()

    #     elif event == cv2.EVENT_MOUSEMOVE and flags & cv2.EVENT_FLAG_LBUTTON:
    #         self.points.append((x, y))
    #         logging.debug("x: {}\ty: {}".format(x, y))
    #         cv2.circle(self.original_img, (x, y), 2, (255, 0, 0), 2)

    #     elif event == cv2.EVENT_LBUTTONUP:
    #         if not self.points:
    #             res = self.translate()
    #             self._display_html(res)
    #             logging.info(res)
    #         else:
    #             if is_closed(self.points):
    #                 print(self.get_slide_paragraph())
    #             else:
    #                 res = self.translate()
    #                 self._display_html(res)
    #                 logging.info(res)

    #         self.x = 0
    #         self.y = 0
    #         self.points = []
    #         logging.debug("x: {}\ty: {}".format(self.x, self.y))
