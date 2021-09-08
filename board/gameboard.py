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

from core.wukong import Wukong
from utils import FileUtil


class Gameboard:
    def __init__(self, width=1920, height=1080, mode='interactive') -> None:
        self.WHITE = (255, 255, 255)
        self.GREEN = (0, 255, 0)
        self.BLUE = (153, 153, 255)
        self.RED = (255, 0, 0)

        self.classifier = Classifier()
        self.wukong = Wukong()
        self.res = {'label': 'unknown', 'descriptor': [], 'line': []}
        self.points = []
        self.auto_label = True
        self.fix_label = False
        self.SAVE_DIR = './output'
        self.MAX_FIX_DIST = 20

        pygame.init()
        self.NAME = "Labelling Tool"
        self.board_width = width
        self.board_height = height
        self.board = pygame.display.set_mode((self.board_width, self.board_height))
        pygame.display.set_caption(self.NAME)
        self.font = pygame.font.SysFont("segoe ui", 60)
        self.PANEL_WIDTH = 1350
        self.scale = self.board_width/1920
        self.board.fill(self.WHITE)


        self.all_btns = []
        self.all_sprites = pygame.sprite.Group()
        self.btn_assist = Button(1740/1920*self.board_width, 135/1080*self.board_height, self.scale,  './res/assist_on.jpg', './res/assist_off.jpg', 'assist', selected=True)
        self.btn_reset = Button(1740/1920*self.board_width, 270/1080*self.board_height, self.scale, './res/reset_on.jpg', './res/reset_off.jpg', 'reset')
        self.btn_save = Button(1500/1920*self.board_width, 135/1080*self.board_height, self.scale, './res/save_on.jpg', './res/save_off.jpg', 'save')
        self.btn_fix = Button(1500/1920*self.board_width, 270/1080*self.board_height, self.scale, './res/hand_label_on.jpg', './res/hand_label_off.jpg', 'fix')

        self.btn_unknown = Button(1500/1920*self.board_width, 450/1080*self.board_height, self.scale, './res/unknown_on.jpg', './res/unknown_off.jpg', 'unknown')
        self.btn_ellipse = Button(1500/1920*self.board_width, 585/1080*self.board_height, self.scale, './res/ellipse_on.jpg', './res/ellipse_off.jpg', 'ellipse')
        self.btn_circle = Button(1500/1920*self.board_width, 720/1080*self.board_height, self.scale, './res/circle_on.jpg', './res/circle_off.jpg', 'circle')
        self.btn_line = Button(1500/1920*self.board_width, 855/1080*self.board_height, self.scale, './res/line_on.jpg', './res/line_off.jpg', 'line')
        self.btn_form = Button(1500/1920*self.board_width, 990/1080*self.board_height, self.scale, './res/form_on.jpg', './res/form_off.jpg', 'form_extension')
        self.btn_tri = Button(1740/1920*self.board_width, 585/1080*self.board_height, self.scale, './res/tri_on.jpg', './res/tri_off.jpg', 'triangle')
        self.btn_quad = Button(1740/1920*self.board_width, 720/1080*self.board_height, self.scale, './res/quad_on.jpg', './res/quad_off.jpg', 'quadrangle')
        self.btn_penta = Button(1740/1920*self.board_width, 855/1080*self.board_height, self.scale, './res/penta_on.jpg', './res/penta_off.jpg', 'pentagon')
        self.btn_hex = Button(1740/1920*self.board_width, 990/1080*self.board_height, self.scale, './res/hex_on.jpg', './res/hex_off.jpg', 'hexagon')

        self.all_btns.append(self.btn_assist)
        self.all_btns.append(self.btn_reset)
        self.all_btns.append(self.btn_save)
        self.all_btns.append(self.btn_fix)
        self.all_btns.append(self.btn_unknown)
        self.all_btns.append(self.btn_form)
        self.all_btns.append(self.btn_line)
        self.all_btns.append(self.btn_tri)
        self.all_btns.append(self.btn_quad)
        self.all_btns.append(self.btn_penta)
        self.all_btns.append(self.btn_hex)
        self.all_btns.append(self.btn_circle)
        self.all_btns.append(self.btn_ellipse)

        for btn in self.all_btns:
            self.all_sprites.add(btn)

        self.LABELS = ['unknown', 'form_extension', 'line', 'triangle', 'quadrangle', 'pentagon', 'hexagon', 'circle', 'ellipse']
        self.label_to_btn = dict(zip(self.LABELS, self.all_btns[4:]))
        self.all_labels = self.all_btns[4:]


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
                    # esc: exit
                    if event.key == 27:
                        pygame.quit()
                        sys.exit()

                    # whitespace: fix
                    if event.key == 32:
                        self.btn_fix.set_state(True)
                        self.fix_label = True
                        self.board.fill(self.WHITE)
                        self.res['descriptor'].clear()
                        for l in self.res['line']:
                            for p in l:
                                pygame.draw.circle(self.board, self.BLUE, p, 3)

                    # c: clear canvas and reset
                    elif event.key == 99:
                        self.btn_reset.set_state(True)
                        self._reset_board()


                    # s: save
                    elif event.key == 115:
                        print(self.res)
                        self.btn_save.set_state(True)
                        self._save_result()
                        self._reset_board()

                elif event.type == pygame.KEYUP:
                    # c: clear
                    if event.key == 99:
                        self.btn_reset.set_state(False)
                        self.btn_fix.set_state(False)

                    # s: save
                    elif event.key == 115:
                        self.btn_save.set_state(False)
                        self.btn_fix.set_state(False)

                if pygame.mouse.get_pos()[0] > self.PANEL_WIDTH * self.scale:
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        logging.debug("pos: {}".format(event.pos))
                        for btn in self.all_btns:
                            if btn.mouse_hover(event.pos):
                                name = btn.get_name()
                                if name == 'reset':
                                    btn.set_state(True)
                                    self._reset_board()
                                elif name == 'save':
                                    print(self.res)
                                    btn.set_state(True)
                                    self._save_result()
                                    self._reset_board()
                                elif name == 'assist':
                                    btn.switch_state()
                                    self.auto_label = not self.auto_label
                                elif name == 'fix':
                                    btn.set_state(True)
                                    self.board.fill(self.WHITE)
                                    self.fix_label = True
                                    self.res['descriptor'].clear()
                                    for l in self.res['line']:
                                        for p in l:
                                            pygame.draw.circle(self.board, self.BLUE, p, 3)
                                else:
                                    btn.switch_state()
                                    if btn.get_state():
                                        self.res['label'] = name
                                        for b in self.all_labels:
                                            if b != btn:
                                                b.set_state(False)

                    elif event.type == pygame.MOUSEBUTTONUP:
                        for btn in self.all_btns:
                            if btn.mouse_hover(event.pos):
                                name = btn.get_name()
                                if name == 'reset':
                                    btn.set_state(False)
                                    self.btn_fix.set_state(False)

                                elif name == 'save':
                                    btn.set_state(False)
                                    self.btn_fix.set_state(False)

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
                            if self.auto_label and len(self.points) > 2:
                                # label, pts = self.classifier.detect(self.points)
                                res = self.wukong.detect(self.points)
                                label = res['label']
                                pts = res['descriptor']
                                self.label_to_btn[label].set_state(True)
                                logging.info("\nlabel: {}\ndescriptor: \n{}".format(label, pts))
                                self.res['label'] = label
                                self.res['descriptor'] = pts.tolist() if pts is not None else []
                                self._draw_result(label, pts)
                            self.points.clear()

            self.all_sprites.draw(self.board)
            pygame.display.flip()


    def _draw_result(self, label, pts):
        pygame.draw.rect(self.board, self.WHITE, (10, 90, 350, 60), width=0)
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
        self.res = {'label': 'unknown', 'descriptor': [], 'line': []}
        self.points.clear()
        self.fix_label = False

        for btn in self.all_labels:
            btn.set_state(False)

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
