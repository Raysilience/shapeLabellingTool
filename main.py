import logging
import math

import numpy as np

from board.gameboard import Gameboard
from board.whiteboard import Whiteboard
from utils import ShapeUtil

if __name__ == '__main__':

    # pts = FileUtil.csv_to_arr('./test/54.csv')
    LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
    logging.basicConfig(level=logging.DEBUG, format=LOG_FORMAT)
    whiteboard = Gameboard()
    # whiteboard = Whiteboard()

    # # whiteboard.set_points(pts)
    whiteboard.draw()

    # vertices = np.asarray([[286, 304], [736, 360], [736, 656], [442, 604]])
    # vertices = ShapeUtil.align_shape(vertices, math.pi/6)
