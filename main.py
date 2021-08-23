import logging
import MathUtil
from whiteboard import Whiteboard
import numpy as np
import math

if __name__ == '__main__':
    # a = np.asarray((1,0))
    # b = np.asarray((0,1))


    LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
    logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)

    whiteboard = Whiteboard()
    whiteboard.draw()