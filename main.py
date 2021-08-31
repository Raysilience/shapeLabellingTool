import logging

import numpy as np

from utils import MathUtil
from whiteboard import Whiteboard

if __name__ == '__main__':


    LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
    logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)

    whiteboard = Whiteboard()
    whiteboard.draw()