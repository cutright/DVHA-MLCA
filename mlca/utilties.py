#!/usr/bin/env python
# -*- coding: utf-8 -*-

# utilities.py
# Copyright (c) 2016-2020 Dan Cutright
# This file is part of DVH Analytics MLC Analyzer, released under a BSD license.
#    See the file LICENSE included with this distribution, also
#    available at https://github.com/cutright/DVHA-MLCA

import numpy as np


def get_xy_path_lengths(shapely_object):
    """
    Get the x and y path lengths of a a Shapely object
    :param shapely_object: either 'GeometryCollection', 'MultiPolygon', or 'Polygon'
    :return: path lengths in the x and y directions
    :rtype: list
    """
    path = np.array([0., 0.])
    if shapely_object.type == 'GeometryCollection':
        for geometry in shapely_object.geoms:
            if geometry.type in {'MultiPolygon', 'Polygon'}:
                path = np.add(path, get_xy_path_lengths(geometry))
    elif shapely_object.type == 'MultiPolygon':
        for shape in shapely_object:
            path = np.add(path, get_xy_path_lengths(shape))
    elif shapely_object.type == 'Polygon':
        x, y = np.array(shapely_object.exterior.xy[0]), np.array(shapely_object.exterior.xy[1])
        path = np.array([np.sum(np.abs(np.diff(x))), np.sum(np.abs(np.diff(y)))])

    return path.tolist()


def flatten_list_of_lists(some_list, remove_duplicates=False, sort=False):
    """
    Convert a list of lists into a list of all values
    :param some_list: a list such that each value is a list
    :type some_list: list
    :param remove_duplicates: if True, return a unique list, otherwise keep duplicated values
    :type remove_duplicates: bool
    :param sort: if True, sort the list
    :type sort: bool
    :return: a new object containing all values in the provided
    """
    data = [item for sublist in some_list for item in sublist]

    if remove_duplicates:
        if sort:
            return list(set(data))
        else:
            ans = []
            for value in data:
                if value not in ans:
                    ans.append(value)
            return ans
    elif sort:
        return sorted(data)

    return data