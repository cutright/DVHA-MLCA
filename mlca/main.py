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
    get_file_paths,
    get_dicom_files,
    create_cmd_parser,
    get_default_output_filename,
)


def process(
    init_dir=None,
    output_file=None,
    print_version=False,
    verbose=False,
    processes=1,
    **kwargs
):
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
    verbose : bool, optional
        Print more detailed information as the script runs
    processes : int
        Number of processes used for multiprocessing
    """

    if print_version:
        print("DVHA MLC Analyzer: dvha-mlca v%s" % __version__)

    if init_dir is not None:

        # command line args are strings
        try:
            processes = int(float(processes))
        except Exception:
            processes = 1

        print("Directory: %s\n" "Begin file tree scan ..." % init_dir)
        file_paths = get_file_paths(init_dir)
        print(
            "File tree scan complete\n" "Searching for DICOM-RT Plan files ..."
        )
        dicom_plan_files = get_dicom_files(
            file_paths,
            modality="RTPLAN",
            verbose=verbose,
            processes=processes,
        )
        print("%s DICOM-RT Plan file(s) found" % len(dicom_plan_files))

        if not output_file:
            output_file = get_default_output_filename()

        kwargs["verbose"] = verbose
        kwargs["processes"] = processes
        print("Analyzing %s file(s) ..." % len(dicom_plan_files))
        plan_analyzer = PlanSet(dicom_plan_files, **kwargs)
        print("Analysis Complete")

        if kwargs["verbose"]:
            print(plan_analyzer.csv.replace(",", "\t"))

        print("Printing summary to: %s" % output_file)
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
