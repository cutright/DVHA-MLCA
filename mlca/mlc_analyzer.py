#!/usr/bin/env python
# -*- coding: utf-8 -*-

# mlc_analyzer.py
"""
Tools for analyzing beam and control point information from DICOM files
Hierarchy of classes: Plan -> FxGroup -> Beam -> ControlPoint
"""
# Copyright (c) 2016-2021 Dan Cutright
# This file is part of DVH Analytics MLC Analyzer, released under a BSD license
#    See the file LICENSE included with this distribution, also
#    available at https://github.com/cutright/DVHA-MLCA

import pydicom
from pydicom.dataset import Dataset
import numpy as np
from shapely.geometry import Polygon
from shapely import speedups
from mlca.utilities import (
    flatten_list_of_lists as flatten,
    get_xy_path_lengths,
    run_multiprocessing,
)
from mlca.options import (
    BEAM_MU_TOLERANCE,
    CONTROL_POINT_MU_TOLERANCE,
    CONTROL_POINT_POS_TOLERANCE,
    DEFAULT_OPTIONS,
)
import warnings


COLUMNS = [
    "Patient Name",
    "Patient MRN",
    "Study Instance UID",
    "SOP Instance UID",
    "TPS",
    "Plan name",
    "# of Fx Group(s)",
    "Fx Group #",
    "Fractions",
    "Plan MUs",
    "Beam Count(s)",
    "Control Point(s)",
    "Complexity Score(s)",
    "File Name",
]


def get_options(over_rides):
    """Get MLC Analyzer options

    Parameters
    ----------
    over_rides : dict
        Over rides, keys may be 'max_field_size_x', 'max_field_size_y',
        'complexity_weight_x', or 'complexity_weight_y'

    Returns
    -------
    dict
        Options for field size and complexity weights. Default values are
        400 and 1.

    """
    options = {k: v for k, v in DEFAULT_OPTIONS.items()}
    for key, value in over_rides.items():
        if key in list(options):
            options[key] = value
    return options


# Enable shapely calculations using C, as opposed to the C++ default
if speedups.available:
    speedups.enable()


class PlanSet:
    """Parse DICOM-RT Plan files, analyze MLCs

    Parameters
    ----------
    file_paths : list
        A list of file paths to DICOM-RT Plan files
    verbose : bool, optional
        Set to true to print detailed information (ignored if
        multiprocessing enabled)
    processes : int
        Number of parallel processes allowed

    """

    def __init__(self, file_paths, verbose=False, processes=1, **kwargs):
        self.file_paths = file_paths
        self.verbose = verbose
        self.processes = processes
        self.kwargs = kwargs
        self.summary_table = [",".join(COLUMNS)]

        if processes == 1:
            try:
                self._run()
            except KeyboardInterrupt:
                print("Plan analyzer halted!")
        else:
            data = run_multiprocessing(
                self._worker, self.file_paths, self.processes
            )
            for row in data:
                self.summary_table.extend(row)

    def _run(self):
        """Process files, accumulate data in self.summary_table"""
        plan_count = len(self.file_paths)
        for i, file_path in enumerate(self.file_paths):
            print("Analyzing (%s of %s): %s" % (i + 1, plan_count, file_path))
            try:
                plan = Plan(file_path, **self.kwargs)
                for fx_grp_row in plan.summary:
                    row = [fx_grp_row[key] for key in COLUMNS]
                    self.summary_table.append(",".join(row))

                if self.verbose:
                    print(plan, "\n")
            except Exception as e:
                print("Analysis failed\n%s\n" % e)

    def _worker(self, file_path):
        """Multiprocessing worker

        Parameters
        ----------
        file_path : str
            file path of a DICOM-RT Plan file

        Returns
        -------
        list
            Results from Plan.summary prepped for CSV output
        """
        data = []
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                plan = Plan(file_path, **self.kwargs)
            for fx_grp_row in plan.summary:
                row = [fx_grp_row[key] for key in COLUMNS]
                data.append(",".join(row))
        except Exception:
            pass
        return data

    @property
    def csv(self):
        """A csv of summary data

        Returns
        -------
        str
            CSV of Plan.summary information
        """
        return "\n".join(self.summary_table)


class Plan:
    """Collect plan information from an RT Plan DICOM file.
    Automatically parses fraction data with FxGroup class

    Parameters
    ----------
    rt_plan : str, Dataset
        file path of a DICOM RT Plan file or a pydicom Dataset

    """

    def __init__(self, rt_plan, **kwargs):

        if isinstance(rt_plan, Dataset):
            self.rt_plan_file = "Unknown"
        else:
            self.rt_plan_file = rt_plan
            rt_plan = pydicom.read_file(rt_plan)
        self.rt_plan = rt_plan

        self.options = get_options(kwargs)

        beam_seq = rt_plan.BeamSequence
        fx_grp_seq = rt_plan.FractionGroupSequence
        self.fx_group = [FxGroup(fx_grp, beam_seq) for fx_grp in fx_grp_seq]

        self.summary = [
            {
                "Patient Name": self.patient_name,
                "Patient MRN": self.patient_id,
                "Study Instance UID": self.study_instance_uid,
                "SOP Instance UID": self.sop_instance_uid,
                "TPS": self.tps,
                "Plan name": self.plan_name,
                "# of Fx Group(s)": str(len(self.fx_group)),
                "Fx Group #": str(f + 1),
                "Fractions": str(fx_grp.fxs),
                "Plan MUs": "%0.1f" % fx_grp.fx_mu,
                "Beam Count(s)": str(fx_grp.beam_count),
                "Control Point(s)": str(sum(fx_grp.cp_counts)),
                "Complexity Score(s)": "%0.3f"
                % self.younge_complexity_scores[f],
                "File Name": self.rt_plan_file,
            }
            for f, fx_grp in enumerate(self.fx_group)
        ]

    def __str__(self):
        summary = [
            "Patient Name:        %s" % self.patient_name,
            "Patient MRN:         %s" % self.patient_id,
            "Study Instance UID:  %s" % self.study_instance_uid,
            "SOP Instance UID:    %s" % self.sop_instance_uid,
            "TPS:                 %s" % self.tps,
            "Plan name:           %s" % self.plan_name,
            "# of Fx Group(s):    %s" % len(self.fx_group),
            "Plan MUs:            %s"
            % ", ".join(["%0.1f" % fx_grp.fx_mu for fx_grp in self.fx_group]),
            "Beam Count(s):       %s"
            % ", ".join([str(fx_grp.beam_count) for fx_grp in self.fx_group]),
            "Control Point(s):    %s"
            % ", ".join(
                [str(sum(fx_grp.cp_counts)) for fx_grp in self.fx_group]
            ),
            "Complexity Score(s): %s"
            % ", ".join(
                ["%0.3f" % cs for cs in self.younge_complexity_scores]
            ),
        ]
        return "\n".join(summary)

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        """Compare to Plan objects

        Parameters
        ----------
        other : Plan

        Returns
        -------
        bool
            True if all properties and FxGrp comparisons are true

        """

        attr = [
            "plan_name",
            "patient_name",
            "patient_id",
            "study_instance_uid",
            "sop_instance_uid",
            "tps",
        ]
        if not all([getattr(self, a) == getattr(other, a) for a in attr]):
            return False

        for i, fx_group in enumerate(self.fx_group):
            if not fx_group == other.fx_group[i]:
                return False
        return True

    @property
    def plan_name(self):
        """Get the plan name

        Returns
        -------
        str
            RTPlanLabel (300A,0002)
        """
        return str(getattr(self.rt_plan, "RTPlanLabel", ""))

    @property
    def patient_name(self):
        """Get the patient name

        Returns
        -------
        str
            PatientName (0010,0010)
        """
        return str(getattr(self.rt_plan, "PatientName", ""))

    @property
    def patient_id(self):
        """Get the patient id

        Returns
        -------
        str
            PatientID (0010,0020)
        """
        return str(getattr(self.rt_plan, "PatientID", ""))

    @property
    def study_instance_uid(self):
        """Get the patient study instance UID

        Returns
        -------
        str
            StudyInstanceUID (0020,000D)
        """
        return str(getattr(self.rt_plan, "StudyInstanceUID", ""))

    @property
    def sop_instance_uid(self):
        """Get the patient study instance UID

        Returns
        -------
        str
            SOPInstanceUID (0008,0018)
        """
        return str(getattr(self.rt_plan, "SOPInstanceUID", ""))

    @property
    def tps(self):
        """Get the treatment planning system

        Returns
        -------
        str
            Manufacturer (0008,0070) and ManufacturerModelName (0008,1090)
        """
        return "%s %s" % (
            getattr(self.rt_plan, "Manufacturer", ""),
            getattr(self.rt_plan, "ManufacturerModelName", ""),
        )

    @property
    def younge_complexity_scores(self):
        """Get the Younge complexity scores for each FxGroup

        Returns
        -------
        list
            FxGroup.younge_complexity_score for each fraction group
        """
        return [
            float(fx_grp.younge_complexity_score) for fx_grp in self.fx_group
        ]


class FxGroup:
    """Collect fraction group information from fraction group and beam
    sequences of a pydicom RT Plan dataset. Automatically parses beam data
    with Beam class

    Parameters
    ----------
    fx_grp_seq : Dataset
        element of FractionGroupSequence (300A,0070)
    plan_beam_sequences : BeamSequence
        BeamSequence (300A,00B0)

    """

    def __init__(self, fx_grp_seq, plan_beam_sequences, **kwargs):
        self.fxs = str(
            getattr(fx_grp_seq, "NumberOfFractionsPlanned", "UNKNOWN")
        )

        self.options = get_options(kwargs)

        meter_set = {}
        for ref_beam in fx_grp_seq.ReferencedBeamSequence:
            ref_beam_num = str(ref_beam.ReferencedBeamNumber)
            meter_set[ref_beam_num] = float(ref_beam.BeamMeterset)

        self.beam = []
        for beam in plan_beam_sequences:
            beam_num = str(beam.BeamNumber)
            if beam_num in meter_set:
                self.beam.append(Beam(beam, meter_set[beam_num]))
        self.update_missing_jaws()

    def __eq__(self, other):
        """Comparison of two FxGroup by comparing each beam

        Parameters
        ----------
        other : FxGroup
            Another FxGroup class object

        Returns
        -------
        bool
            True if all properties and Beam comparisons are true
        """

        attr = [
            "beam_count",
            "beam_names",
            "beam_mu",
            "fx_mu",
            "cp_counts",
            "younge_complexity_score",
        ]
        if not all([getattr(self, a) == getattr(other, a) for a in attr]):
            return False

        for i, beam in enumerate(self.beam):
            status_str = "beam %s\n\t%%s with other beam %s" % (
                self.beam_names[i],
                other.beam_names[i],
            )
            if not beam == other.beam[i]:
                print(status_str % "failed")
                return False
            else:
                print(status_str % "passed")
        return True

    @property
    def beam_count(self):
        """Get the number of beams

        Returns
        -------
        int
            Length of FxGroup.beams
        """
        return len(self.beam)

    @property
    def beam_names(self):
        """Get the beam names

        Returns
        -------
        list
            Beam.name for each beam
        """
        return [b.name for b in self.beam]

    @property
    def beam_mu(self):
        """Get the monitor units for each beam

        Returns
        -------
        list
            Beam.meter_set for each beam
        """
        return [b.meter_set for b in self.beam]

    @property
    def fx_mu(self):
        """Get the number of MU for for this fraction

        Returns
        -------
        float
            The sum of FxGroup.beam_mu
        """
        return np.sum(self.beam_mu)

    @property
    def cp_counts(self):
        """Get the number of control points for all beams

        Returns
        -------
        list
            Beam.cp_count for each beam
        """
        return [b.cp_count for b in self.beam]

    @property
    def younge_complexity_score(self):
        """Get the Younge complexity score this fraction

        Returns
        -------
        float
            The sum of Beam.younge_complexity_scores for all beams
        """
        return np.sum(
            np.array(
                [np.sum(beam.younge_complexity_scores) for beam in self.beam]
            )
        )

    def update_missing_jaws(self):
        """In plans with static jaws, jaw positions may
        not be found in each control point"""
        for i, beam in enumerate(self.beam):
            for j, cp in enumerate(beam.jaws):
                if (
                    cp["x_min"] == -self.options["max_field_size_x"] / 2
                    and cp["x_max"] == self.options["max_field_size_x"] / 2
                    and cp["y_min"] == -self.options["max_field_size_y"] / 2
                    and cp["y_max"] == self.options["max_field_size_y"] / 2
                ):
                    beam.jaws[j] = beam.jaws[0]


class Beam:
    """Collect beam information from a beam in a beam sequence of a pydicom
    RT Plan dataset. Automatically parses control point data with ControlPoint
    class

    Parameters
    ----------
    beam_dataset : Dataset
        element of a BeamSequence (300A,00B0)
    meter_set : int, float
        the monitor units for ``beam_dataset``
    ignore_zero_mu_cp : bool
        If True, skip over zero MU control points
        (e.g., as in Step-N-Shoot beams)

    """

    def __init__(
        self, beam_dataset, meter_set, ignore_zero_mu_cp=False, **kwargs
    ):
        self.beam_dataset = beam_dataset
        self.meter_set = meter_set
        self.ignore_zero_mu_cp = ignore_zero_mu_cp
        self.options = get_options(kwargs)

        self.control_point = [
            ControlPoint(cp, self.leaf_boundaries) for cp in self.cp_seq
        ]

        self.summary = {
            "cp": list(range(1, len(self.control_point) + 1)),
            "cum_mu_frac": [cp.cum_mu for cp in self.control_point],
            "cum_mu": self.cum_mu,
            "cp_mu": self.cp_mu,
            "gantry": self.gantry_angle,
            "collimator": self.collimator_angle,
            "couch": self.couch_angle,
            "jaw_x1": [j["x_min"] for j in self.jaws],
            "jaw_x2": [j["x_max"] for j in self.jaws],
            "jaw_y1": [j["y_min"] for j in self.jaws],
            "jaw_y2": [j["y_max"] for j in self.jaws],
            "area": self.area,
            "x_perim": self.perimeter_x,
            "y_perim": self.perimeter_y,
            "perim": self.perimeter,
            "cmp_score": self.younge_complexity_scores.tolist(),
        }

        for key in self.summary:
            if len(self.summary[key]) == 1:
                self.summary[key] = self.summary[key] * len(self.summary["cp"])

        if ignore_zero_mu_cp:
            non_zero_indices = [
                i
                for i, value in enumerate(self.summary["cp_mu"])
                if value != 0
            ]
            for key in list(self.summary):
                self.summary[key] = [
                    self.summary[key][i] for i in non_zero_indices
                ]

    def __eq__(self, other):
        """Compare ControlPoint classes in two beams

        Parameters
        ----------
        other : Beam
            Another Beam instance for comparison

        Returns
        -------
        bool
            True if same meter_set values and each paired ControlPoint elements
            evaluate as equal
        """
        if (self.meter_set - other.meter_set) > BEAM_MU_TOLERANCE:
            return False
        for i, cp in enumerate(self.control_point):
            if not cp == other.control_point[i]:
                print("cp %s failed" % i)
                return False
        return True

    @property
    def leaf_boundaries(self):
        """Get the leaf boundaries

        Returns
        -------
        DataSet
            LeafPositionBoundaries (300A,00BE)
        """
        for bld_seq in self.beam_dataset.BeamLimitingDeviceSequence:
            if hasattr(bld_seq, "LeafPositionBoundaries"):
                return bld_seq.LeafPositionBoundaries

    @property
    def aperture(self):
        """Get aperture shapely object for every control point

        Returns
        -------
        list
            ControlPoint.aperture for each control point

        """
        return [cp.aperture for cp in self.control_point]

    @property
    def name(self):
        """Get the Beam name

        Returns
        -------
        str
            In order of priority, BeamDescription (300A,00C3),
            BeamName (300A,00C2), or "Unknown"
        """
        return str(
            getattr(
                self.beam_dataset,
                "BeamDescription",
                getattr(self.beam_dataset, "BeamName", "Unknown"),
            )
        )

    @property
    def perimeter_x(self):
        """Get x-component of aperture perimeter for every control point

        Returns
        -------
        list
            ControlPoint.perimeter_x for each control point

        """
        return np.array([cp.perimeter_x for cp in self.control_point])

    @property
    def perimeter_y(self):
        """Get y-component of aperture perimeter for every control point

        Returns
        -------
        list
            ControlPoint.perimeter_y for each control point

        """
        return np.array([cp.perimeter_y for cp in self.control_point])

    @property
    def perimeter(self):
        """Get aperture perimeter for every control point

        Returns
        -------
        list
            ControlPoint.perimeter for each control point

        """
        return np.array([cp.perimeter for cp in self.control_point])

    @property
    def area(self):
        """Get aperture area for every control point

        Returns
        -------
        list
            ControlPoint.area for each control point

        """
        return [cp.area for cp in self.aperture]

    @property
    def cp_seq(self):
        """Get the control points

        Returns
        -------
        Dataset
            ControlPointSequence (300A,0111)
        """
        return self.beam_dataset.ControlPointSequence

    @property
    def cp_count(self):
        """Get the number of control points in this beam

        Returns
        -------
        int
            Length of ControlPointSequence (300A,0111)
        """
        return len(self.cp_seq)

    @property
    def jaws(self):
        """Jaw positions for each control point

        Returns
        -------
        list
            Each element is a ControlPoint.jaws dict
        """
        return [cp.jaws for cp in self.control_point]

    @property
    def cp_mu(self):
        """MU for each control point

        Returns
        -------
        np.ndarray
            Numpy array of control point MUs
        """
        return np.diff(np.array(self.cum_mu)).tolist() + [0]

    @property
    def mlc_borders(self):
        """Get the MLC border for each control point

        Returns
        -------
        list
            A list of ``ControlPoint.mlc_borders`` describing the boundaries of
            each leaf
        """
        return [cp.mlc_borders for cp in self.control_point]

    @property
    def gantry_angle(self):
        """Gantry angles for each control point

        Returns
        -------
        list
            A list of float values, defining gantry angles for each
            control point

        """
        return [
            float(cp.GantryAngle)
            for cp in self.cp_seq
            if hasattr(cp, "GantryAngle")
        ]

    @property
    def collimator_angle(self):
        """Collimator angles for each control point

        Returns
        -------
        list
            A list of float values, defining collimator angles for each
            control point

        """
        return [
            float(cp.BeamLimitingDeviceAngle)
            for cp in self.cp_seq
            if hasattr(cp, "BeamLimitingDeviceAngle")
        ]

    @property
    def couch_angle(self):
        """Couch angles for each control point

        Returns
        -------
        list
            A list of float values, defining couch angles for each
            control point

        """
        return [
            float(cp.PatientSupportAngle)
            for cp in self.cp_seq
            if hasattr(cp, "PatientSupportAngle")
        ]

    @property
    def cum_mu(self):
        """Cumulative monitor units for each control point

        Returns
        -------
        list
            A list of float values representing the cumulative MU
        """
        return [cp.cum_mu * self.meter_set for cp in self.control_point]

    @property
    def younge_complexity_scores(self):
        """Complexity score based on Younge et al

        Returns
        -------
        np.ndarray
            Younge complexity scores for each control point
        """
        # Complexity score based on:
        # Younge KC, Matuszak MM, Moran JM, McShan DL, Fraass BA,
        # Roberts DA. Penalization of aperture complexity in inversely planned
        # volumetric modulated arc therapy. Med Phys. 2012;39(11):7160–70.
        c1, c2 = (
            self.options["complexity_weight_x"],
            self.options["complexity_weight_y"],
        )
        if self.meter_set and self.meter_set > 0:
            return (
                np.divide(
                    np.multiply(
                        np.add(c1 * self.perimeter_x, c2 * self.perimeter_y),
                        self.cp_mu,
                    ),
                    self.area,
                )
                / self.meter_set
            )
        return 0


class ControlPoint:
    """Collect control point information from a ControlPointSequence in a beam
    dataset of a pydicom RT Plan dataset

    Parameters
    ----------
    cp_elem : DataElement
        element of a ControlPointSequence (300A,0111)
    leaf_boundaries : Dataset
        LeafPositionBoundaries (300A,00BE)

    """

    def __init__(self, cp_elem, leaf_boundaries, **kwargs):

        self.cp_elem = cp_elem
        self.leaf_boundaries = leaf_boundaries
        self.options = get_options(kwargs)

        self._set_leaf_jaw_type()

        self.path_lengths = get_xy_path_lengths(self.aperture)

    def _set_leaf_jaw_type(self):
        """Search for LeafJawPositions (300A,011C) assign
        ControlPoint.<RTBeamLimitingDeviceType (300A,00B8)>
        (i.e., x, y, asymx, asymy, mlcx, mlcy)
        Return type is ``np.ndarray`` or ``None`` for all"""

        if hasattr(self.cp_elem, "BeamLimitingDevicePositionSequence"):
            for (
                device_position_seq
            ) in self.cp_elem.BeamLimitingDevicePositionSequence:
                if hasattr(
                    device_position_seq, "RTBeamLimitingDeviceType"
                ) and hasattr(device_position_seq, "LeafJawPositions"):
                    leaf_jaw_type = str(
                        device_position_seq.RTBeamLimitingDeviceType
                    ).lower()
                    positions = np.array(
                        list(map(float, device_position_seq.LeafJawPositions))
                    )
                    mid_index = int(len(positions) / 2)
                    setattr(
                        self,
                        leaf_jaw_type,
                        [positions[:mid_index], positions[mid_index:]],
                    )

    @property
    def cum_mu(self):
        """Cumulative MU for this ControlPoint

        Returns
        -------
        float
            CumulativeMetersetWeight (300A,0134)

        """
        return float(self.cp_elem.CumulativeMetersetWeight)

    @property
    def mlc(self):
        """Get the MLC orientation

        Returns
        -------
        str, None
            Returns 'mlcx', 'mlcy' or ``None``
        """
        for leaf_type in ["mlcx", "mlcy"]:
            if hasattr(self, leaf_type):
                return getattr(self, leaf_type)

    @property
    def leaf_type(self):
        """Get the MLC orientation

        Returns
        -------
        str, None
            Returns 'mlcx', 'mlcy' or ``None``
        """
        for leaf_type in ["mlcx", "mlcy"]:
            if hasattr(self, leaf_type):
                return leaf_type

    @property
    def perimeter_x(self):
        """x-component of the aperture perimeter

        Returns
        -------
        float
            x-component of the Aperture perimeter
        """
        return self.path_lengths[0]

    @property
    def perimeter_y(self):
        """y-component of the aperture perimeter

        Returns
        -------
        float
            y-component of the Aperture perimeter
        """
        return self.path_lengths[1]

    @property
    def perimeter(self):
        """Perimeter of the aperture

        Returns
        -------
        float
            Aperture perimeter
        """
        return self.perimeter_x + self.perimeter_y

    def __eq__(self, other):
        """Compare to ControlPoint class objects

        Parameters
        ----------
        other : ControlPoint

        Returns
        -------
        bool
            True if cum_mu and each MLC position are with tolerance
        """

        if abs(self.cum_mu - other.cum_mu) > CONTROL_POINT_MU_TOLERANCE:
            return False
        for side in [0, 1]:
            for i, pos in enumerate(self.mlc[side]):
                if abs(pos - other.mlc[side][i]) > CONTROL_POINT_POS_TOLERANCE:
                    print(abs(pos - other.mlc[side][i]))
        return True

    @property
    def mlc_borders(self):
        """This function returns the boundaries of each MLC leaf for purposes
        of displaying a beam's eye view using bokeh's quad() glyph

        Returns
        -------
        dict
            the boundaries of each leaf within the control point with keys of
            'top', 'bottom', 'left', 'right

        """
        if self.mlc is not None:
            top = self.leaf_boundaries[0:-1] + self.leaf_boundaries[0:-1]
            top = [float(i) for i in top]
            bottom = self.leaf_boundaries[1::] + self.leaf_boundaries[1::]
            bottom = [float(i) for i in bottom]
            left = [-self.options["max_field_size_x"] / 2] * len(self.mlc[0])
            left.extend(self.mlc[1])
            right = self.mlc[0].tolist()
            right.extend(
                [self.options["max_field_size_x"] / 2] * len(self.mlc[1])
            )

            return {"top": top, "bottom": bottom, "left": left, "right": right}

    @property
    def aperture(self):
        """This function will return the outline of MLCs within jaws

        Returns
        -------
        Polygon
            a shapely object of the complete MLC aperture as one shape
            (including MLC overlap)

        """
        lb = self.leaf_boundaries
        mlc = self.mlc

        jaws = self.jaws
        jaw_points = [
            (jaws["x_min"], jaws["y_min"]),
            (jaws["x_min"], jaws["y_max"]),
            (jaws["x_max"], jaws["y_max"]),
            (jaws["x_max"], jaws["y_min"]),
        ]
        jaw_shapely = Polygon(jaw_points)

        if self.leaf_type == "mlcx":
            a = flatten(
                [[(m, lb[i]), (m, lb[i + 1])] for i, m in enumerate(mlc[0])]
            )
            b = flatten(
                [[(m, lb[i]), (m, lb[i + 1])] for i, m in enumerate(mlc[1])]
            )
        elif self.leaf_type == "mlcy":
            a = flatten(
                [[(lb[i], m), (lb[i + 1], m)] for i, m in enumerate(mlc[0])]
            )
            b = flatten(
                [[(lb[i], m), (lb[i + 1], m)] for i, m in enumerate(mlc[1])]
            )
        else:
            return jaw_shapely

        mlc_points = a + b[::-1]  # concatenate a and reverse(b)
        mlc_aperture = Polygon(mlc_points).buffer(0)

        # This function is very slow, since jaws are rectangular, perhaps
        # there's a more efficient method?
        aperture = mlc_aperture.intersection(jaw_shapely)

        return aperture

    @property
    def jaws(self):
        """Get the jaw positions of a control point

        Returns
        -------
        dict
            jaw positions (or max field size in lieu of a jaw). Keys are
            'x_min', 'x_max', 'y_min', 'y_max'

        """

        jaws = {}

        for dim in ["x", "y"]:
            half = self.options["max_field_size_%s" % dim] / 2.0
            values = getattr(self, "asym%s" % dim, [-half, half])
            jaws["%s_min" % dim] = float(min(values))
            jaws["%s_max" % dim] = float(max(values))

        return jaws
