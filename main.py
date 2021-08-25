import logging

import MathUtil
from whiteboard import Whiteboard

if __name__ == '__main__':
    # print(MathUtil.polar_to_cartesian((30, 2)))

    LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
    logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)

    whiteboard = Whiteboard()
    whiteboard.draw()