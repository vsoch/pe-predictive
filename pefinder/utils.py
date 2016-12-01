from logman import logger
import os
import pandas
import sys


######################################################################################
# Supporting functions
######################################################################################

def load_reports(reports_path,report_field=None,id_field=None,delim=None):
    '''load_reports will load a report from a path. If the path is a folder,
    the files in the folder are treated as individual reports, with the filename
    corresponding to an id, and the text inside the report text. If the reports_path
    is a file, it is assumed to be a .tsv (tab separated values) file with columns
    report_id and report_text
    :param reports_path: the path to the reports folder or .tsv file
    :param report_field: the field to use (default is report_text)
    :param delim: the delimiter separating the columns of the reports file
    '''
    reports_path = os.path.abspath(reports_path)
    if not os.path.exists(reports_path):
        logger.error("Cannot find file or folder at %s, does it exist?",reports_path)
        sys.exit(1)

    if report_field == None:
        report_field = "report_text"
    if id_field == None:
        id_field = "report_id"
    if delim == None:
        delim = "\t"

    logger.info("reports path provided is %s",reports_path)

    # For a directory, read in the reports
    if os.path.isdir(reports_path):
        report_files = glob("%s/*" %(reports_path))
        reports = pandas.DataFrame(columns=[report_field])        
        for report_file in report_files:
            report_id = os.path.basename(report_file).split('.')[0]
            try:
                reports.loc[report_id] = read_file(report_file)
            except:
                logger.warning("Problem reading report %s",report_file)

    # For a file, read in assuming tab separation
    elif os.path.isfile(reports_path):
        reports = pandas.read_csv(reports_path,
                                  sep=delim)

    else:
        logger.error("A path to a reports file or folder with reports must be provided.")
        sys.exit(1)

    # Ensure that reports object has correct headers
    check_header(reports,
                 headers=[report_field,id_field])

    return reports


def check_header(reports,headers):
    '''check_header will ensure that one or more header fields are present
    in a pandas data frame.
    :param headers: a single (or list) of headers
    '''
    if isinstance(headers,str):
        headers = [headers]
    for header in headers:
        if header not in reports.columns:
            logger.error('Required header %s not found in reports file. Exiting',header) 
            sys.exit(1)


def read_file(file_path,mode='r'):
    '''read_file will read in a file and return the contents
    :param file_path: the path to the file
    '''
    with open(file_path,mode) as filey:
        content = filey.read()
    return content
