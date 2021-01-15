#!/usr/bin/env python
# -*- coding: utf-8 -*-

# main.py
"""
Collect DICOM-RT Plan Files, save summary to .csv
"""
# Copyright (c) 2016-2021 Dan Cutright
# This file is part of DVH Analytics MLC Analyzer, released under a BSD license
#    See the file LICENSE included with this distribution, also
#    available at https://github.com/cutright/DVHA-MLCA

from mlca.mlc_analyzer import PlanSet
from mlca._version import __version__
from mlca.utilities import (
    get_dicom_files,
    create_cmd_parser,
    get_default_output_filename,
)


def process(init_dir=None, output_file=None, print_version=False, **kwargs):
    """Process command line args, call mlc_analyzer.PlanSet

    Parameters
    ----------
    init_dir : str
         Directory containing DICOM-RT Plan files
    output_file : str, optional
         Output will be saved as dvha_mlca_<version>_results_<time-stamp>.csv
         by default.
    print_version : bool, optional
         Print the DVHA-MLCA version

    """

    if print_version:
        print("DVHA MLC Analyzer: dvha-mlca v%s" % __version__)

    if init_dir is not None:

        kwargs["file_paths"] = get_dicom_files(
            init_dir, modality="RTPLAN", verbose=kwargs["verbose"]
        )
        plan_analyzer = PlanSet(**kwargs)

        if kwargs["verbose"]:
            print(plan_analyzer.csv.replace(",", "\t"))

        if not output_file:
            output_file = get_default_output_filename()
        with open(output_file, "w") as doc:
            doc.write(plan_analyzer.csv)

    elif not print_version:
        print("mlca: error: the following arguments are required: init_dir")


def main():
    """Parse command-line args, pass into process"""
    cmd_parser = create_cmd_parser()
    kwargs = vars(cmd_parser.parse_args())
    process(**kwargs)


if __name__ == "__main__":
    main()
