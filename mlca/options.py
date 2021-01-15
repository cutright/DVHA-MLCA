#!/usr/bin/env python
# -*- coding: utf-8 -*-

# options.py
"""
Misc options for dvha-mlca
"""
# Copyright (c) 2016-2021 Dan Cutright
# This file is part of DVH Analytics MLC Analyzer, released under a BSD license
#    See the file LICENSE included with this distribution, also
#    available at https://github.com/cutright/DVHA-MLCA


BEAM_MU_TOLERANCE = 0.001
CONTROL_POINT_MU_TOLERANCE = 0.00001
CONTROL_POINT_POS_TOLERANCE = 0.0001

DEFAULT_OPTIONS = {
    "max_field_size_x": 400.0,
    "max_field_size_y": 400.0,
    "complexity_weight_x": 1.0,
    "complexity_weight_y": 1.0,
}
