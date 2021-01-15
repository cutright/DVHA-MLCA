#!/usr/bin/env python
# -*- coding: utf-8 -*-

# utilities.py
"""
Utilities for DVHA-MLCA
"""
# Copyright (c) 2016-2021 Dan Cutright
# This file is part of DVH Analytics MLC Analyzer, released under a BSD license
#    See the file LICENSE included with this distribution, also
#    available at https://github.com/cutright/DVHA-MLCA

import argparse
from datetime import datetime
from mlca._version import __version__
import numpy as np
import pydicom
import os
from mlca.options import DEFAULT_OPTIONS


def get_xy_path_lengths(shapely_object):
    """Get the x and y path lengths of a Shapely object

    Parameters
    ----------
    shapely_object : GeometryCollection, MultiPolygon, Polygon
        A shapely polygon-like object

    Returns
    -------
    list
        Perimeter lengths in the x and y directions

    """
    path = np.array([0.0, 0.0])
    if shapely_object.type == "GeometryCollection":
        for geometry in shapely_object.geoms:
            if geometry.type in {"MultiPolygon", "Polygon"}:
                path = np.add(path, get_xy_path_lengths(geometry))
    elif shapely_object.type == "MultiPolygon":
        for shape in shapely_object:
            path = np.add(path, get_xy_path_lengths(shape))
    elif shapely_object.type == "Polygon":
        x, y = np.array(shapely_object.exterior.xy[0]), np.array(
            shapely_object.exterior.xy[1]
        )
        path = np.array(
            [np.sum(np.abs(np.diff(x))), np.sum(np.abs(np.diff(y)))]
        )

    return path.tolist()


def flatten_list_of_lists(some_list, remove_duplicates=False, sort=False):
    """Convert a list of lists into one list of all values

    Parameters
    ----------
    some_list : list
        a list such that each element is a list
    remove_duplicates : bool, optional
        if True, return a unique list, otherwise keep duplicated values
    sort : bool, optional
        if True, sort the list

    Returns
    -------
    list
        A new list containing all values in ``some_list``

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


def get_file_paths(init_dir):
    """Find all files in a directory and sub-directories

    Parameters
    ----------
    init_dir : str
        Top-level directory to search for files

    Returns
    -------
    list
        Absolute file paths

    """
    file_paths = []
    # iterate through files and all sub-directories
    for dirName, subdirList, fileList in os.walk(init_dir):
        for file_name in fileList:
            file_paths.append(os.path.join(dirName, file_name))
    return file_paths


def is_file_dicom(file_path, modality=None, verbose=False):
    """

    Parameters
    ----------
    file_path : str
        File path to potential DICOM file
    modality : str, optional
        Return False if file is not this Modality (0008,0060)
    verbose : bool, optional
        Print results to terminal

    Returns
    -------
    bool
        True if file_path points to a DICOM file, will return False if
        SOPClassUID (0008,0016) is not found

    """
    kwargs = {"stop_before_pixels": True, "force": True}
    try:
        ds = pydicom.read_file(file_path, **kwargs)
        # Assuming SOPClassUID is a required tag
        if modality is None and "SOPClassUID" in ds:
            if verbose:
                print("DICOM File Found: %s" % file_path)
            return True
        if ds.Modality.upper() == modality.upper():
            if verbose:
                print("DICOM %s File Found: %s" % (modality, file_path))
            return True
    except Exception as e:
        if verbose:
            print("Non-DICOM File Found: %s" % file_path)
            print(str(e))
    return False


def get_dicom_files(init_dir, modality=None, verbose=False):
    """Find all DICOM-RT Plan files in a directory and sub-directories

    Parameters
    ----------
    init_dir : str
        Top-level directory to search for DICOM-RT Plan files
    modality : str, optional
        Specify Modality (0008,0060)
    verbose : bool, optional
        Print results to terminal

    Returns
    -------
    list
        Absolute file paths to DICOM-RT Plans

    """
    if verbose:
        print("Finding DICOM-RT Plans in %s ..." % init_dir)
    file_paths = get_file_paths(init_dir)
    rt_plans = [f for f in file_paths if is_file_dicom(f, modality, verbose)]
    if verbose:
        print("DICOM-RT Plan search complete")
    return rt_plans


def create_cmd_parser():
    """Get an argument parser for mlca.main

    Returns
    -------
    argparse.ArgumentParser
        argument parser
    """
    cmd_parser = argparse.ArgumentParser(
        description="Command line DVHA MLC Analyzer"
    )
    cmd_parser.add_argument(
        "init_dir",
        nargs="?",
        help="Directory containing DICOM-RT Plan files",
        default=None,
    )
    cmd_parser.add_argument(
        "-of",
        "--output-file",
        dest="output_file",
        help="Output will be saved as dvha_mlca_<version>_results_"
        "<time-stamp>.csv by default.",
        default=None,
    )
    cmd_parser.add_argument(
        "-xw",
        "--x-weight",
        dest="complexity_weight_x",
        help="Complexity coefficient for x-dimension: default = %0.1f"
        % DEFAULT_OPTIONS["complexity_weight_x"],
        default=DEFAULT_OPTIONS["complexity_weight_x"],
    )
    cmd_parser.add_argument(
        "-yw",
        "--y-weight",
        dest="complexity_weight_y",
        help="Complexity coefficient for y-dimension: default = %0.1f"
        % DEFAULT_OPTIONS["complexity_weight_y"],
        default=DEFAULT_OPTIONS["complexity_weight_y"],
    )
    cmd_parser.add_argument(
        "-xs",
        "--x-max-field-size",
        dest="max_field_size_x",
        help="Maximum field size in the x-dimension: default = %0.1f (mm)"
        % DEFAULT_OPTIONS["max_field_size_x"],
        default=DEFAULT_OPTIONS["max_field_size_x"],
    )
    cmd_parser.add_argument(
        "-ys",
        "--y-max-field-size",
        dest="max_field_size_y",
        help="Maximum field size in the y-dimension: default = %0.1f (mm)"
        % DEFAULT_OPTIONS["max_field_size_y"],
        default=DEFAULT_OPTIONS["max_field_size_y"],
    )
    cmd_parser.add_argument(
        "-ver",
        "--version",
        dest="print_version",
        help="Print the DVHA-MLCA version",
        default=False,
        action="store_true",
    )
    cmd_parser.add_argument(
        "-v",
        "--verbose",
        dest="verbose",
        help="Print final results and plan summaries as they are analyzed",
        default=False,
        action="store_true",
    )

    return cmd_parser


def get_default_output_filename():
    """Get the default output file name for mlca.main.process

    Returns
    -------
    str
        dvha_mlca_<version>_results_<timestamp>.csv
    """
    time_stamp = str(datetime.now()).replace(":", "-").replace(".", "-")
    return "dvha_mlca_%s_results_%s.csv" % (
        __version__,
        time_stamp,
    )
