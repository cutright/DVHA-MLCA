#!/usr/bin/env python
# -*- coding: utf-8 -*-

# main.py
"""
Collect DICOM-RT Plan Files, save summary to .csv
"""
# Copyright (c) 2016-2020 Dan Cutright
# This file is part of DVH Analytics MLC Analyzer, released under a BSD license.
#    See the file LICENSE included with this distribution, also
#    available at https://github.com/cutright/DVHA-MLCA

import argparse
from datetime import datetime
import os
import pydicom
from mlca.mlc_analyzer import Plan, DEFAULT_OPTIONS, COLUMNS
from mlca._version import __version__


class PlanSet:
    def __init__(self, file_paths, **kwargs):

        verbose = 'verbose' in kwargs and kwargs['verbose']

        self.plans = []
        plan_count = len(file_paths)
        for i, file_path in enumerate(file_paths):
            print('Analyzing (%s of %s): %s' % (i+1, plan_count, file_path))
            self.plans.append(Plan(file_path, **kwargs))
            if verbose:
                print(self.plans[-1], '\n')

        self.summary_table = [','.join(COLUMNS)]
        for plan in self.plans:
            for fx_grp_row in plan.summary:
                row = [fx_grp_row[key] for key in COLUMNS]
                self.summary_table.append(','.join(row))

    @property
    def csv(self):
        return '\n'.join(self.summary_table)


def get_file_paths(init_dir):
    print('Finding DICOM-RT Plans in %s ...' % init_dir)
    file_paths = []
    for dirName, subdirList, fileList in os.walk(init_dir):  # iterate through files and all sub-directories
        for file_name in fileList:
            file_path = os.path.join(dirName, file_name)
            try:
                is_valid = pydicom.read_file(file_path, stop_before_pixels=True, force=True).Modality == 'RTPLAN'
                if is_valid:
                    file_paths.append(file_path)
            except Exception:
                print('Non-DICOM-RT File Found, skipping analysis: %s' % file_path)
    print('DICOM-RT Plan search complete')
    return file_paths


def main():
    cmd_parser = argparse.ArgumentParser(description="Command line DVHA MLC Analyzer")
    cmd_parser.add_argument('init_dir', nargs='?',
                            help='Directory containing DICOM-RT Plan files',
                            default=None)
    cmd_parser.add_argument('-of', '--output-file',
                            dest='output_file',
                            help='Output will be saved as dvha_mlca_<version>_results_<time-stamp>.csv by default.',
                            default=None)
    cmd_parser.add_argument('-xw', '--x-weight',
                            dest='complexity_weight_x',
                            help='Complexity coefficient for x-dimension: default = %0.1f' %
                                 DEFAULT_OPTIONS['complexity_weight_x'],
                            default=DEFAULT_OPTIONS['complexity_weight_x'])
    cmd_parser.add_argument('-yw', '--y-weight',
                            dest='complexity_weight_y',
                            help='Complexity coefficient for y-dimension: default = %0.1f' %
                                 DEFAULT_OPTIONS['complexity_weight_y'],
                            default=DEFAULT_OPTIONS['complexity_weight_y'])
    cmd_parser.add_argument('-xs', '--x-max-field-size',
                            dest='max_field_size_x',
                            help='Maximum field size in the x-dimension: default = %0.1f (mm)' %
                                 DEFAULT_OPTIONS['max_field_size_x'],
                            default=DEFAULT_OPTIONS['max_field_size_x'])
    cmd_parser.add_argument('-ys', '--y-max-field-size',
                            dest='max_field_size_y',
                            help='Maximum field size in the y-dimension: default = %0.1f (mm)' %
                                 DEFAULT_OPTIONS['max_field_size_y'],
                            default=DEFAULT_OPTIONS['max_field_size_y'])
    cmd_parser.add_argument('-ver', '--version',
                            dest='print_version',
                            help='Print the DVHA-MLCA version',
                            default=False,
                            action='store_true')
    cmd_parser.add_argument('-v', '--verbose',
                            dest='verbose',
                            help='Print the DVHA-MLCA version',
                            default=False,
                            action='store_true')
    args = cmd_parser.parse_args()

    if args.print_version:
        print('DVHA MLC Analyzer: dvha-mlca v%s' % __version__)

    if args.init_dir is not None:
        cmd_options = {key: getattr(args, key) for key in list(DEFAULT_OPTIONS)}
        cmd_options['file_paths'] = get_file_paths(args.init_dir)

        time_stamp = str(datetime.now()).replace(':', '-').replace('.', '-')
        default_file = "dvha_mlca_%s_results_%s.csv" % (__version__, time_stamp)
        output_file = args.output_file if args.output_file is not None else default_file

        plan_analyzer = PlanSet(**cmd_options)

        if args.verbose:
            print(plan_analyzer.csv.replace(',', '\t'))

        with open(output_file, 'w') as doc:
            doc.write(plan_analyzer.csv)
    elif not args.print_version:
        print("mlca: error: the following arguments are required: init_dir")


if __name__ == '__main__':
    main()
