#!usr/bin/env python
# coding utf-8
'''
@File       :wukong.py
@Copyright  :CV Group
@Date       :9/8/2021
@Author     :Rui
@Desc       :
'''
import logging
import math

from core.classifier import Classifier
from core.fitter import Fitter
from core.regularizer import Regularizer
from core.trajectory import Trajectory
from utils import ShapeUtil


class Wukong:
    def __init__(self, reg_on=True):
        self.reg_on = reg_on
        self.MIN_BALL_RADIUS = 50
        self.MIN_DISTINGUISH_ANGLE = math.cos(math.pi / 6)
        self.NUM_OF_CONSECUTIVE_POINTS = 15
        self.MAX_CLOSED_FACTOR = 0.4
        self.CONVEX_RELAXATION = math.pi/6

        self.LABELS = ['unknown', 'form_extension', 'line', 'triangle', 'quadrangle', 'pentagon', 'hexagon', 'circle',
                       'ellipse']

        self.classifier = Classifier()
        self.fitter = Fitter()
        self.regularizer = Regularizer()

        self.parts = set()

    def detect(self, points):
        label = "unknown"
        sub_label = ''
        descriptor = []
        trajectory = Trajectory(points)

        # one touch drawing
        if trajectory.is_closed(self.MAX_CLOSED_FACTOR):
            label = self.classifier.detect_shape(trajectory)
            descriptor = self.fitter.fit(label, trajectory)
            # end-to-end strategy
            # label, descriptor = self.classifier.detect_end2end(trajectory)
            if self.reg_on:
                sub_label, descriptor = self.regularizer.regularize(label, descriptor)

        # multi touches drawing
        else:
            _points = self.classifier.find_turning_points(points)
            trajectory = Trajectory(_points)
            if ShapeUtil.is_convex(_points, self.CONVEX_RELAXATION):
                custom_label, custom_descriptor = self.classifier.detect_customized_shape(trajectory)

                # concatenate trajectories
                for part in list(self.parts):
                    traj, cnt_match = trajectory.match(part)
                    logging.debug("number of matched points: {}\n".format(cnt_match))

                    if traj is not None and ShapeUtil.is_convex(traj.points):
                        if cnt_match == 1:
                            self.parts.add(traj)
                        elif cnt_match == 2:
                            label = self.classifier.detect_shape(traj)
                            descriptor = self.fitter.fit(label, traj)
                            if self.reg_on:
                                sub_label, descriptor = self.regularizer.regularize(label, descriptor)
                if len(descriptor) == 0 and len(custom_descriptor) != 0:
                    label = custom_label
                    descriptor = custom_descriptor

        return {'label': label, 'sub_label': sub_label, 'descriptor': descriptor}
