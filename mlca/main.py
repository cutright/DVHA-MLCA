#!/usr/bin/env python
# -*- coding: utf-8 -*-

# main.py
"""
Collect DICOM-RT Plan Files, save summary to .csv
"""
# Copyright (c) 2016-2020 Dan Cutright
# This file is part of DVH Analytics MLC Analyzer, released under a BSD license
#    See the file LICENSE included with this distribution, also
#    available at https://github.com/cutright/DVHA-MLCA

import argparse
from datetime import datetime
from mlca.mlc_analyzer import PlanSet, DEFAULT_OPTIONS
from mlca._version import __version__
from mlca.utilities import get_file_paths


def main(
    init_dir=None,
    output_file=None,
    verbose=False,
    print_version=False,
    **kwargs
):
    """

    Parameters
    ----------
    init_dir : str
         Directory containing DICOM-RT Plan files
    output_file : str, optional
         Output will be saved as dvha_mlca_<version>_results_<time-stamp>.csv
         by default.
    verbose : bool, optional
         Print final results and plan summaries as they are analyzed
    print_version : bool, optional
         Print the DVHA-MLCA version

    """

    if print_version:
        print("DVHA MLC Analyzer: dvha-mlca v%s" % __version__)

    if init_dir is not None:

        kwargs["init_dir"] = init_dir
        kwargs["output_file"] = output_file
        kwargs["verbose"] = verbose
        kwargs["file_paths"] = get_file_paths(init_dir)

        time_stamp = str(datetime.now()).replace(":", "-").replace(".", "-")
        default_file = "dvha_mlca_%s_results_%s.csv" % (
            __version__,
            time_stamp,
        )
        output_file = output_file if output_file is not None else default_file

        plan_analyzer = PlanSet(**kwargs)

        if verbose:
            print(plan_analyzer.csv.replace(",", "\t"))

        with open(output_file, "w") as doc:
            doc.write(plan_analyzer.csv)
    elif not print_version:
        print("mlca: error: the following arguments are required: init_dir")


if __name__ == "__main__":
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
        help="Output will be saved as dvha_mlca_<version>_results_<time-stamp>.csv by default.",
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
    args = vars(cmd_parser.parse_args())
    main(**args)
