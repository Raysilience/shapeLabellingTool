#!usr/bin/env python
# coding utf-8
'''
@File       :gameboard.py
@Copyright  :CV Group
@Date       :9/2/2021
@Author     :Rui
@Desc       :
'''
import json
from datetime import datetime

import numpy as np
import logging

from board.button import Button
from core.classifier import Classifier
import pygame
import sys

from utils import FileUtil


class Gameboard:
    def __init__(self, width=1920, height=1080, mode='interactive') -> None:
        self.WHITE = (255, 255, 255)
        self.GREEN = (0, 255, 0)
        self.BLUE = (0, 0, 255)
        self.RED = (255, 0, 0)

        self.classifier = Classifier()
        self.res = {'label': 'unknown', 'descriptor': [], 'line': []}
        self.points = []
        self.auto_label = True
        self.fix_label = False
        self.SAVE_DIR = '../output'
        self.MAX_FIX_DIST = 20

        pygame.init()
        self.NAME = "Labelling Tool"
        self.board_width = width
        self.board_height = height
        self.board = pygame.display.set_mode((self.board_width, self.board_height))
        self.board.fill(self.WHITE)
        pygame.display.set_caption(self.NAME)
        self.font = pygame.font.Font(None, 60)

        self.PANEL_WIDTH = 1300

        self.all_btns = pygame.sprite.Group()
        self.btn_assist = Button(1740, 135, './res/assist_on.jpg', './res/assist_off.jpg')
        self.btn_reset = Button(1740, 270, './res/reset_on.jpg', './res/reset_off.jpg')
        self.btn_save = Button(1500, 135, './res/save_on.jpg', './res/save_off.jpg')
        self.btn_fix = Button(1500, 270, './res/hand_label_on.jpg', './res/hand_label_off.jpg')

        self.btn_unknown = Button(1500, 450, './res/unknown_on.jpg', './res/unknown_off.jpg')
        self.btn_ellipse = Button(1500, 585, './res/ellipse_on.jpg', './res/ellipse_off.jpg')
        self.btn_circle = Button(1500, 720, './res/circle_on.jpg', './res/circle_off.jpg')
        self.btn_line = Button(1500, 855, './res/line_on.jpg', './res/line_off.jpg')
        self.btn_form = Button(1500, 990, './res/form_on.jpg', './res/form_off.jpg')
        self.btn_tri = Button(1740, 585, './res/tri_on.jpg', './res/tri_off.jpg')
        self.btn_quad = Button(1740, 720, './res/quad_on.jpg', './res/quad_off.jpg')
        self.btn_penta = Button(1740, 855, './res/penta_on.jpg', './res/penta_off.jpg')
        self.btn_hex = Button(1740, 990, './res/hex_on.jpg', './res/hex_off.jpg')


        self.all_btns.add(self.btn_assist)
        self.all_btns.add(self.btn_reset)
        self.all_btns.add(self.btn_save)
        self.all_btns.add(self.btn_fix)
        self.all_btns.add(self.btn_line)
        self.all_btns.add(self.btn_tri)
        self.all_btns.add(self.btn_quad)
        self.all_btns.add(self.btn_penta)
        self.all_btns.add(self.btn_hex)
        self.all_btns.add(self.btn_circle)
        self.all_btns.add(self.btn_ellipse)
        self.all_btns.add(self.btn_form)
        self.all_btns.add(self.btn_unknown)



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
                        self.board.fill(self.WHITE)
                        self.fix_label = True
                        self.res['descriptor'].clear()
                        for l in self.res['line']:
                            for p in l:
                                pygame.draw.circle(self.board, self.BLUE, p, 3)

                    # c: clear
                    elif event.key == 99:
                        self._reset_board()

                    # s: save
                    elif event.key == 115:
                        print(self.res)
                        self._save_result()
                        self._reset_board()

                if pygame.mouse.get_pos()[0] > self.PANEL_WIDTH:
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        logging.debug("pos: {}".format(event.pos))
                        for btn in self.all_btns:
                            btn.update(pos=event.pos)

                else:
                    if self.fix_label:
                        if event.type == pygame.MOUSEBUTTONDOWN:
                            pt = self._find_closest_on_path(event.pos)
                            self.res['descriptor'].append(pt)
                            pygame.draw.circle(self.board, self.RED, pt, 7, 3)
                    else:
                        if event.type == pygame.MOUSEMOTION and event.buttons[0]:
                            self.points.append(event.pos)
                            pygame.draw.circle(self.board, self.BLUE, event.pos, 3)

                        elif event.type == pygame.MOUSEBUTTONUP:
                            self.res['line'].append(list(self.points))
                            if len(self.points) > 2:
                                label, pts = self.classifier.detect(self.points)
                                logging.info("\nlabel: {}\ndescriptor: \n{}".format(label, pts))
                                self.res['label'] = label
                                self.res['descriptor'] = pts.tolist() if pts is not None else []
                                self._draw_result(label, pts)
                            self.points.clear()

            self.all_btns.draw(self.board)
            pygame.display.flip()

    def _draw_result(self, label, pts):
        label_img = self.font.render(label, True, self.RED, self.WHITE)
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

    def _reset_board(self):
        self.board.fill(self.WHITE)
        self.fix_label = not self.auto_label
        self.res = {'label': 'unknown', 'descriptor': [], 'line': []}
        self.points.clear()

    def _save_result(self):
        FileUtil.mkdir(self.SAVE_DIR)
        filename = "{}/{}_{}.json".format(self.SAVE_DIR, self.res['label'], datetime.now().strftime('%Y%m%d%H%M%S'))
        print(filename)
        with open(filename, 'w') as f:
            json.dump(self.res, f)

    def _find_closest_on_path(self, point):
        ans = None
        prev_dist = 0xFFFF
        for l in self.res['line']:
            for p in l:
                dist = np.linalg.norm(np.asarray(point) - np.asarray(p), 1)
                if dist < min(self.MAX_FIX_DIST, prev_dist):
                    ans = p
                    prev_dist = dist
        return ans if ans else point
