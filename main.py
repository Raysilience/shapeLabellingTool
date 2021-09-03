import logging

from board.gameboard import Gameboard


if __name__ == '__main__':

    # # pts = FileUtil.csv_to_arr('./test/54.csv')
    #
    LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
    logging.basicConfig(level=logging.DEBUG, format=LOG_FORMAT)
    #
    whiteboard = Gameboard(mode='interactive')
    # # whiteboard.set_points(pts)
    whiteboard.draw()

