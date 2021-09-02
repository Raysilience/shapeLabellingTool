import logging
import math

import numpy as np

from utils import MathUtil, FileUtil
from whiteboard import Whiteboard

if __name__ == '__main__':

    # pts = FileUtil.csv_to_arr('./test/54.csv')

    LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
    logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)

    whiteboard = Whiteboard(mode='interactive')
    # whiteboard.set_points(pts)
    whiteboard.draw()