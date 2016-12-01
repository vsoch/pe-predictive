from logman import logger
import os
import pandas
import sys

colors={"pulmonary_embolism":"blue",
       "definite_negated_existence":"red",
       "probable_negated_existence":"indianred",
       "ambivalent_existence":"orange",
       "probable_existence":"forestgreen",
       "definite_existence":"green",
       "historical":"goldenrod",
       "indication":"Pink",
       "acute":"golden"}


######################################################################################
# Supporting functions
######################################################################################

def load_reports(reports_path):
    '''load_reports will load a report from a path. If the path is a folder,
    the files in the folder are treated as individual reports, with the filename
    corresponding to an id, and the text inside the report text. If the reports_path
    is a file, it is assumed to be a .tsv (tab separated values) file with columns
    report_id and report_text
    :param reports_path: the path to the reports folder or .tsv file
    '''
    reports_path = os.path.abspath(reports_path)

    # For a directory, read in the reports
    if os.path.isdir(reports_path):
        report_files = glob("%s/*" %(reports_path))
        reports = pandas.DataFrame(columns=['report_text'])        
        for report_file in report_files:
            report_id = os.path.basename(report_file).split('.')[0]
            try:
                reports.loc[report_id] = read_file(report_file)
            except:
                logger.warning("Problem reading report %s",report_file)

    # For a file, read in assuming tab separation
    elif os.path.isfile(reports_path):
        reports = pandas.read_csv(reports_path,
                                  sep="\t",
                                  header=True)

    else:
        logger.error("A path to a reports file or folder with reports must be provided.")
         sys.exit(1)

    # Ensure that reports object has correct headers
    check_header(reports,
                 headers=["report_text","report_id"])

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
            logging.error('Required header %s not found in reports file. Exiting',headear) 
            sys.exit(1)


def read_file(file_path,mode='r'):
    '''read_file will read in a file and return the contents
    :param file_path: the path to the file
    '''
    with open(file_path,mode) as filey:
        content = filey.read()
    return content
