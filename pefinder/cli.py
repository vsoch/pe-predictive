#!/usr/bin/env python3

import argparse
from glob import glob
from logman import logger
import pickle
import os
import sys
from utils import load_reports

from pefinder import (
    mark_reports, 
    analyze_reports,
    label_remapping
)


def get_parser():

    parser = argparse.ArgumentParser(description="generate predictions for PE for a set of reports (impressions)")

    # Name of the docker image, required
    parser.add_argument("--reports", 
                        dest='reports', 
                        help="Path to folder of reports, or tab separated text file", 
                        type=str,
                        required=True)

    parser.add_argument("--report_field", 
                        dest='report_field', 
                        help="the header column that contains the text of interest (default is report_text)", 
                        type=str,
                        default="report_text")

    parser.add_argument("--id_field", 
                        dest='id_field', 
                        help="the header column that contains the id of the report (default is report_id)", 
                        type=str,
                        default="report_id")

    parser.add_argument("--result_field", 
                        dest='result_field', 
                        help="the field to save pefinder (chapman) result to, not saved unless --no-remap is specified.", 
                        type=str,
                        default="pe_result")

    parser.add_argument("--delim", 
                        dest='delim', 
                        help="the delimiter separating the input reports data. Default is tab (\\t)", 
                        type=str,
                        default="\t")

    parser.add_argument("--output", 
                        dest='output', 
                        help="Desired output file (.tsv)", 
                        type=str,
                        required=True)

    parser.add_argument("--verbose", 
                        dest='verbose', 
                        help="Print more verbose output (useful for analyzing more reports)", 
                        action='store_true',
                        required=False)

    parser.add_argument('--no-remap',
                        dest='remapping',
                        help="don't remap multilabel PEFinder result to Stanford labels",
                        default=True,
                        action='store_false')

    parser.add_argument('--run',
                        dest="actions",
                        help="mark (mark), or classify (classify) reports.",
                        choices=['classify','mark'],
                        default='classify')

    return parser



def main():
    parser = get_parser()
    
    try:
        args = parser.parse_args()
    except:
        sys.exit(0)

    # Tell the user what is going to be used, in case is incorrect
    logger.info("\n***STARTING PE-FINDER CONTAINER****")
    logger.info("Will use column %s as report text.",args.report_field)
    logger.info("Will use column %s as report id.",args.id_field)
    logger.info("Verbosity set to %s.",args.verbose)

    # Load the reports
    reports = load_reports(reports_path=args.reports,
                           report_field=args.report_field,
                           id_field=args.id_field,
                           delim=args.delim)

    # What actions does the user want to run?
    if "classify" == args.actions:
        reports = analyze_reports(reports,
                                  result_field=args.result_field,
                                  verbose=args.verbose)

        # Remap to Stanford labels (default True)
        if args.remapping == True:
            reports = label_remapping(reports=reports,
                                      result_field=args.result_field,
                                      drop_result=True)

    elif "mark" == args.actions:
        reports = mark_reports(reports,
                               verbose=args.verbose)

    # Parse result in some format, provide visualization? 
    reports.to_csv(args.output,sep="\t",index=False)
    logger.info("Result for %s saved to %s",args.actions,args.output)    

if __name__ == '__main__':
    main()
