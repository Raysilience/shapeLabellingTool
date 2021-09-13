#!usr/bin/env python
# coding utf-8
'''
@File       :risc.py
@Copyright  :CV Group
@Date       :9/8/2021
@Author     :Rui
@Desc       :
'''
import json
import logging
import math

from core.classifier import Classifier
from core.fitter import Fitter
from core.regularizer import Regularizer
from core.trajectory import Trajectory
from utils import ShapeUtil
from configparser import ConfigParser

class RISC:
    """
    Realtime Intelligent Sketch Classifier (RISC) is an online, efficient detector of hand-painted geometric shapes.
    """
    def __init__(self):
        config = ConfigParser()
        config.read("config.ini")
        params = config['params']
        self.reg_on = params.getboolean('REGULARIZER_ON')
        self.MAX_CLOSED_FACTOR = params.getfloat('MAX_CLOSED_FACTOR')
        self.CONVEX_RELAXATION = params.getint('CONVEX_RELAXATION') * math.pi / 180

        self.classifier = Classifier(config)
        self.fitter = Fitter()
        self.regularizer = Regularizer(config)

        self.parts = set()

    def detect(self, points):
        label = "unknown"
        sub_label = ''
        descriptor = []
        trajectory = Trajectory(points)

        # one touch drawing
        if trajectory.is_closed(self.MAX_CLOSED_FACTOR):
            logging.debug("close criterion: sketch is closed")
            label, sub_label, descriptor = self._detect_one_touch(trajectory)

        # multi touches drawing
        else:
            _points = self.classifier.find_turning_points(points)
            trajectory = Trajectory(_points)
            if ShapeUtil.is_convex(_points, self.CONVEX_RELAXATION):
                logging.debug("convex criterion: sketch is closed")

                custom_label, custom_descriptor = self.classifier.detect_customized_shape(trajectory)

                # concatenate trajectories
                for part in list(self.parts):
                    traj, cnt_match = trajectory.match(part)
                    logging.debug("number of matched points: {}\n".format(cnt_match))

                    if traj is not None and ShapeUtil.is_convex(traj.points):
                        if cnt_match == 1:
                            self.parts.add(traj)
                        elif cnt_match == 2:
                            label, sub_label, descriptor = self._detect_one_touch(trajectory)

                if len(descriptor) == 0 and len(custom_descriptor) != 0:
                    label = custom_label
                    descriptor = custom_descriptor

        res = {'label': label, 'sub_label': sub_label, 'descriptor': descriptor}
        return json.dumps(res)

    def _detect_one_touch(self, trajectory):
        sub_label = ''
        # strategy 0: use traditional algorithm or cnn as both classifier and fitter
        label, descriptor = self.classifier.detect_shape(trajectory)

        # strategy 1: use cnn as classifier
        # label = self.classifier.detect_shape(trajectory)
        # descriptor = self.fitter.fit(label, trajectory)

        if self.reg_on and len(descriptor) > 0 :
            sub_label, descriptor = self.regularizer.regularize(label, descriptor)

        return label, sub_label, descriptor
