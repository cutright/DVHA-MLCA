#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# test_mlc_analyzer.py
"""unittest cases for mlc_analyzer."""
#
# Copyright (c) 2020 Dan Cutright
# This file is part of DVHA-MLCA, released under a MIT license.
#    See the file LICENSE included with this distribution, also
#    available at https://github.com/cutright/DVHA-MLCA


import unittest
from os.path import join
from mlca import mlc_analyzer, utilities
import pydicom
import json
from numpy.testing import assert_array_equal, assert_array_almost_equal

test_dir = "tests"
basedata_dir = join(test_dir, "testdata")
example_file_name = "rtplan.dcm"
example_file_path = join(basedata_dir, example_file_name)
mlc_borders_file = join(basedata_dir, "mlc_borders.json")
beam_summary_file = join(basedata_dir, "beam_summary.json")
plan_summary_file = join(basedata_dir, "plan_summary.json")


class TestUtilities(unittest.TestCase):
    """Unit tests for Utilities."""

    def setUp(self):
        """Setup files and base data for utility testing."""
        self.data_path = "example_file_path"

        self.plan_ds = pydicom.read_file(example_file_path)

        with open(mlc_borders_file, "r") as fp:
            self.expected_mlc_borders = json.load(fp)

        with open(beam_summary_file, "r") as fp:
            self.expected_beam_summary = json.load(fp)

        with open(plan_summary_file, "r") as fp:
            self.expected_plan_summary = json.load(fp)

    def test_get_options(self):
        """Test get_options"""
        over_rides = {
            "max_field_size_x": 200,
            "max_field_size_y": 300,
            "complexity_weight_x": 0.5,
            "complexity_weight_y": 0.9,
        }
        self.assertEqual(over_rides, mlc_analyzer.get_options(over_rides))

        self.assertEqual(
            mlc_analyzer.DEFAULT_OPTIONS, mlc_analyzer.get_options({})
        )

        bad_over_rides = {"max_field_size_x": 200, "max_field_size_z": 300}
        expected = {
            key: value for key, value in mlc_analyzer.DEFAULT_OPTIONS.items()
        }
        expected["max_field_size_x"] = 200
        self.assertEqual(expected, mlc_analyzer.get_options(bad_over_rides))

    def test_control_point(self):
        """Test ControlPoint"""
        beam = self.plan_ds.BeamSequence[0]
        bld_seq = beam.BeamLimitingDeviceSequence
        leaf_boundaries = bld_seq[2].LeafPositionBoundaries

        cp = beam.ControlPointSequence[0]
        mlca_cp = mlc_analyzer.ControlPoint(cp, leaf_boundaries)

        # Compare jaw positions
        jaws = mlca_cp.jaws
        self.assertEqual(-78.1, jaws["x_min"])
        self.assertEqual(87.3, jaws["x_max"])
        self.assertEqual(-90.0, jaws["y_min"])
        self.assertEqual(100.0, jaws["y_max"])

        # Compare various aperture properties
        aperture = mlca_cp.aperture
        self.assertAlmostEqual(16172.0, aperture.area)
        self.assertAlmostEqual(770.7999999999998, aperture.length)
        self.assertAlmostEqual(27.931121691813, aperture.centroid.xy[0][0])
        self.assertAlmostEqual(14.66423447934702, aperture.centroid.xy[1][0])

        # check mlc borders compared to test data
        for key, value in mlca_cp.mlc_borders.items():
            assert_array_equal(self.expected_mlc_borders["0"][key], value)

        # CP comparison
        cp_2 = beam.ControlPointSequence[2]
        mlca_cp_2 = mlc_analyzer.ControlPoint(cp_2, leaf_boundaries)
        self.assertTrue(mlca_cp == mlca_cp)
        self.assertFalse(mlca_cp == mlca_cp_2)

    def test_beam(self):
        """Test Beam class"""
        expected_mu = 90.199996948242  # extracted from reference beam
        beam = mlc_analyzer.Beam(self.plan_ds.BeamSequence[0], expected_mu)

        # check beam summary to test data
        for key, value in beam.summary.items():
            assert_array_almost_equal(
                self.expected_beam_summary["0"][key], value
            )

        # check mlc borders compared to test data
        for key, value in beam.mlc_borders[0].items():
            assert_array_equal(self.expected_mlc_borders["0"][key], value)

        # compare two beams
        self.assertTrue(beam == beam)

        beam_wrong_mu = mlc_analyzer.Beam(self.plan_ds.BeamSequence[0], 1)
        self.assertFalse(beam == beam_wrong_mu)

        beam_2 = mlc_analyzer.Beam(self.plan_ds.BeamSequence[1], expected_mu)
        self.assertFalse(beam == beam_2)

        # test ignore zero MU CPs
        beam_no_zero = mlc_analyzer.Beam(
            self.plan_ds.BeamSequence[0], expected_mu, ignore_zero_mu_cp=True
        )
        exp_no_zero = [
            mu for mu in self.expected_beam_summary["0"]["cp_mu"] if mu > 0
        ]
        assert_array_equal(exp_no_zero, beam_no_zero.summary["cp_mu"])

    def test_fx_group(self):
        """Test of the FxGroup class"""
        beam_seq = self.plan_ds.BeamSequence
        fx_grp_seq = self.plan_ds.FractionGroupSequence
        fx_grp_1 = mlc_analyzer.FxGroup(fx_grp_seq[0], beam_seq)
        fx_grp_2 = mlc_analyzer.FxGroup(fx_grp_seq[1], beam_seq)
        self.assertFalse(fx_grp_1 == fx_grp_2)
        self.assertTrue(fx_grp_1 == fx_grp_1)

        self.assertEqual(9, fx_grp_1.beam_count)
        self.assertEqual(90.20, round(fx_grp_1.beam_mu[0], 2))
        self.assertEqual("rpo 200", fx_grp_1.beam_names[0])
        exp_cp_counts = [18, 10, 12, 14, 16, 16, 14, 20, 20]
        self.assertEqual(exp_cp_counts, fx_grp_1.cp_counts)
        self.assertEqual(776.10, round(fx_grp_1.fx_mu, 2))
        self.assertEqual("26", fx_grp_1.fxs)
        self.assertEqual(1.2742, round(fx_grp_1.younge_complexity_score, 4))

    def test_plan(self):
        """Test Plan class"""
        plan = mlc_analyzer.Plan(self.plan_ds)

        # test plan properties
        self.assertEqual("ANON11264", plan.patient_name)
        self.assertEqual("ANON11264", plan.patient_id)
        self.assertEqual("ADAC Pinnacle3", plan.tps)
        exp_cmp = [1.2741877055788196, 1.2897372167540244, 1.1271716301248724]
        assert_array_equal(exp_cmp, plan.younge_complexity_scores)

        # test plan equality comparison
        self.assertTrue(plan == plan)
        self.assertTrue(str(plan) == plan.__repr__())

        ds2 = pydicom.read_file(example_file_path)
        ds2.StudyInstanceUID = "test"
        plan_2 = mlc_analyzer.Plan(ds2)
        self.assertFalse(plan == plan_2)

        plan_2 = mlc_analyzer.Plan(self.plan_ds)
        plan_2.fx_group[0] = plan_2.fx_group[1]
        self.assertFalse(plan == plan_2)

        plan = mlc_analyzer.Plan(example_file_path)
        for i, fx_summary in enumerate(self.expected_plan_summary):
            for key, value in fx_summary.items():
                self.assertEqual(value, plan.summary[i][key])

    def test_plan_set(self):
        """Test PlanSet"""
        files = utilities.get_file_paths(test_dir)
        dcm_files = utilities.get_dicom_files(files, verbose=True)
        plan_set = mlc_analyzer.PlanSet(dcm_files, verbose=True)
        summary = plan_set.csv.split("\n")
        self.assertTrue(len(summary) == 4)

        # Test _worker
        data = plan_set._worker(dcm_files[0])
        self.assertTrue(len(data) == 3)

    def test_plan_set_multiprocessing(self):
        """Test PlanSet with multiprocessing"""
        files = utilities.get_file_paths(test_dir)
        dcm_files = utilities.get_dicom_files(files, processes=2)
        plan_set = mlc_analyzer.PlanSet(dcm_files, verbose=True, processes=2)
        summary = plan_set.csv.split("\n")
        self.assertTrue(len(summary) == 4)
