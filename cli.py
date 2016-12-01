#!/usr/bin/env python3

import argparse
from glob import glob
from logman import logger
import pickle
import os
from utils import load_reports

from pefinder import (
    mark_reports, 
    classify_reports, 
    analyze_reports
)


def get_parser():

    parser = argparse.ArgumentParser(description="generate predictions for PE for a set of reports (impressions)")

    # Name of the docker image, required
    parser.add_argument("--reports", 
                        dest='reports', 
                        help="Path to folder of reports, or tab separated text file", 
                        type=str,
                        required=True)

    parser.add_argument('--clean', action='store_true')
    parser.add_argument('actions', nargs="+",
                        choices=['mark', 'classify','all'],
                        default='all')

    return parser



def main():
    logger.info("\n***STARTING PE-FINDER DOCKER****")
    parser = get_parser()
    
    try:
        args = parser.parse_args()
    except:
        logger.error("Input args to %s improperly set, exiting.", os.path.abspath(__file__))
        parser.print_help()
        sys.exit(0)


    # Load the reports
    reports = load_reports(args.reports)

    # What actions does the user want to run?
    if "all" in args.actions:
        cls = analyze_report(reports)
    
    elif "mark" in args.actions:
        cls = mark_report(reports):

    elif "classify" in args.actions:
        cls = classify_report(reports):

    #TODO:
    # Parse result in some format, provide visualization? 

    

if __name__ == '__main__':
    main()
