import logging

import MathUtil
from whiteboard import Whiteboard

if __name__ == '__main__':
    # print(MathUtil.calc_intersect((0, 0), (0.5, 1), (1, 0), (1,1)))


    LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
    logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)

    whiteboard = Whiteboard()
    whiteboard.draw()