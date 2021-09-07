#!usr/bin/env python
# coding utf-8
'''
@File       :button.py
@Copyright  :CV Group
@Date       :9/3/2021
@Author     :Rui
@Desc       :
'''
import logging

import pygame


class Button(pygame.sprite.Sprite):
    def __init__(self, x, y, scale, img_check_path, img_uncheck_path, name, selected=False):
        pygame.sprite.Sprite.__init__(self)
        self.WHITE = (255, 255, 255)
        self.GREEN = (0, 255, 0)
        self.BLUE = (0, 0, 255)
        self.RED = (255, 0, 0)

        self.scale = scale
        self.selected = selected
        self.font = pygame.font.SysFont("segoe ui", 60)
        self.img_check = pygame.image.load(img_check_path).convert()
        self.img_check = pygame.transform.scale(self.img_check, self.get_size(self.img_check.get_rect()))
        self.img_uncheck = pygame.image.load(img_uncheck_path).convert()
        self.img_uncheck = pygame.transform.scale(self.img_uncheck, self.get_size(self.img_uncheck.get_rect()))

        if self.selected:
            self.image = self.img_check
        else:
            self.image = self.img_uncheck

        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        logging.debug("rect{}".format(self.rect))
        self.xmin = self.rect.x
        self.xmax = self.rect.x + self.rect.w
        self.ymin = self.rect.y
        self.ymax = self.rect.y + self.rect.h
        self.name = name
        logging.debug("name{}".format(self.name))


    def update(self, *args, **kwargs) -> None:
        if 'pos' in kwargs and self.mouse_hover(kwargs['pos']):
            self.switch_state()

    def mouse_hover(self, pos):
        mouse_x, mouse_y = pos
        return self.xmin < mouse_x < self.xmax and self.ymin < mouse_y < self.ymax

    def get_state(self):
        return self.selected

    def set_state(self, flag):
        self.selected = flag
        if self.selected:
            self.image = self.img_check
        else:
            self.image = self.img_uncheck

    def switch_state(self):
        self.set_state(not self.selected)

    def get_name(self):
        return self.name

    def draw(self, surface):
        surface.blit(self.image, self.rect)

    def get_size(self, rect):
        return int(rect.w * self.scale), int(rect.h * self.scale)