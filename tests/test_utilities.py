#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# test_utilities.py
"""unittest cases for utilities."""
#
# Copyright (c) 2020 Dan Cutright
# This file is part of DVHA-MLCA, released under a MIT license.
#    See the file LICENSE included with this distribution, also
#    available at https://github.com/cutright/DVHA-MLCA


import unittest
from os.path import join, basename
from mlca import utilities
from shapely.geometry import GeometryCollection, MultiPolygon, Polygon

test_dir = "tests"
basedata_dir = join(test_dir, "testdata")
example_file_name = "rtplan.dcm"
example_file_path = join(basedata_dir, example_file_name)


class TestUtilities(unittest.TestCase):
    """Unit tests for Utilities."""

    def setUp(self):
        """Setup files and base data for utility testing."""
        self.data_path = example_file_path

    def test_flatten_list_of_lists(self):
        """Test flatten_list_of_lists"""

        # keep all elements
        data = [[1, 10], [3, 5], [2, 3]]
        expected = [1, 10, 3, 5, 2, 3]
        calculated = utilities.flatten_list_of_lists(data)
        self.assertEqual(expected, calculated)

        # remove duplicates
        expected = [1, 10, 3, 5, 2]
        calculated = utilities.flatten_list_of_lists(
            data, remove_duplicates=True
        )
        self.assertEqual(expected, calculated)

        # sorted
        expected = [1, 2, 3, 3, 5, 10]
        calculated = utilities.flatten_list_of_lists(data, sort=True)
        self.assertEqual(expected, calculated)

        # sorted and removed duplicates
        expected = [1, 2, 3, 5, 10]
        calculated = utilities.flatten_list_of_lists(
            data, remove_duplicates=True, sort=True
        )
        self.assertEqual(expected, calculated)

    def test_get_dicom_files(self):
        """Test get_dicom_rt_plan_files"""
        files = utilities.get_dicom_files(test_dir, verbose=True)
        self.assertTrue(len(files) == 1)
        self.assertEqual(basename(self.data_path), basename(files[0]))

        files = utilities.get_dicom_files(test_dir, "RTPLAN", True)
        self.assertTrue(len(files) == 1)
        self.assertEqual(basename(self.data_path), basename(files[0]))

    def test_get_xy_path_lengths(self):
        """Test get_xy_path_lengths"""
        # paths lengths -> x = 2, y = 4
        polygon = Polygon([[0, 0], [1, 0], [1, 2], [0, 2], [0, 0]])

        # paths lengths -> x = 4, y = 8
        multi_polygon = MultiPolygon([polygon, polygon])

        # paths lengths -> x = 6, y = 12
        collection = GeometryCollection([multi_polygon, polygon])

        path_lengths = utilities.get_xy_path_lengths(collection)
        self.assertEqual([6.0, 12.0], path_lengths)
