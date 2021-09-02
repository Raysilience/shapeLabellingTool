#!usr/bin/env python
# coding utf-8
'''
@File       :gameboard.py
@Copyright  :CV Group
@Date       :9/2/2021
@Author     :Rui
@Desc       :
'''
import numpy as np
import logging
from core.classifier import Classifier
import pygame
import os
import sys


class Gameboard:
    def __init__(self, width=960, height=640, mode='interactive') -> None:
        self.WHITE = (255, 255, 255)
        self.GREEN = (0, 255, 0)
        self.BLUE = (0, 0, 255)
        self.RED = (255, 0, 0)
        self.NAME = "Labelling Tool"

        pygame.init()
        self.board_width = width
        self.board_height = height
        self.board = pygame.display.set_mode((self.board_width, self.board_height))
        self.board.fill(self.WHITE)
        pygame.display.set_caption(self.NAME)
        self.font = pygame.font.Font(None, 60)


        self.res = {'label': 'unknown', 'descriptor': [], 'line': []}
        self.points = []
        self.classifier = Classifier()
        self.mode = mode

    def set_points(self, points):
        self.points = points

    def draw(self):

        while True:

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYDOWN:
                    logging.debug("pressed key: {}".format(event.key))

                    # esc
                    if event.key == 27:
                        pygame.quit()
                        sys.exit()

                    # whitespace
                    elif event.key == 32:
                        pass

                    # s: save
                    elif event.key == 115:
                        print(self.res)

                if event.type == pygame.MOUSEMOTION and event.buttons[0]:
                    self.points.append(event.pos)
                    pygame.draw.circle(self.board, self.BLUE, event.pos, 3)

                elif event.type == pygame.MOUSEBUTTONUP:
                    self.res['line'].append(list(self.points))
                    if len(self.points) > 2:
                        label, pts = self.classifier.detect(self.points)
                        logging.info("\nlabel: {}\ndescriptor: \n{}".format(label, pts))
                        self.res['label'] = label
                        self.res['descriptor'] = pts.tolist() if pts is not None else None
                        self._draw_result(label, pts)
                    self.points.clear()

                pygame.display.flip()

    def _draw_result(self, label, pts):
        label_img = self.font.render(label, True, self.RED)
        self.board.blit(label_img, (10, 100))
        if label == 'unknown':
            return
        elif label == 'circle':
            x, y, r = pts
            pygame.draw.circle(self.board, self.GREEN, (x, y), r, 3)
            pygame.draw.circle(self.board, self.RED, (x, y), 3)
        else:
            for p in pts:
                pygame.draw.circle(self.board, self.RED, p, 7, 3)
            pygame.draw.lines(self.board, self.GREEN, True, pts, width=3)
