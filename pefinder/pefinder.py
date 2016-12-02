import radnlp
import networkx as nx

import pyConTextNLP.pyConTextGraph as pyConText
import pyConTextNLP.itemData as itemData
import pickle

import radnlp.classifier as classifier
from radnlp.data import classrslts 
import radnlp.io  as rio
import radnlp.rules as rules
import radnlp.schema as schema
import radnlp.split as split
import radnlp.utils as utils
import radnlp.view as rview

from logman import logger
import json
import sys

logger.info("radnlp version %s",radnlp.__version__)

def load_knowledge_base():
    '''load_knowledge_base returns the Chapman knowledge base,
    which currently is picked using python 3 (and works in this container
    with python3, does not work for python version under that)
    '''
    return pickle.load(open('data/kb.pkl','rb'))

######################################################################################
# Single Report Functions
######################################################################################


def mark_report(report, kb=None):
    '''mark_report will take a report, modifiers, and targets, and
    create a pyConTextGraph object with context markup
    :param report: an individual report's text
    :param kb: the knowledge base
    '''
    if kb==None:
        kb = load_knowledge_base()

    markup = utils.mark_report(split.get_sentences(report),
                               kb['modifiers'],
                               kb['targets'])
    return markup


def classify_report(markup, kb=None):
    '''classify_report will use the rules in the knowledge base to classify
    a new report.
    :param markup: the marked up report, returned from mark_report
    :param kb: the knowledge base
    '''
    if kb==None:
        kb = load_knowledge_base()

    return classifier.classify_document_targets(markup,
                                                 kb['rules'][0],
                                                 kb['rules'][1],
                                                 kb['rules'][2],
                                                 kb['schema'])

def analyze_report(report, kb=None):
    """
    given an individual radiology report, creates a pyConTextGraph
    object that contains the context markup
    report: a text string containing the radiology reports
    """
    if kb == None:
        kb = load_knowledge_base()

    markup = mark_report(report, kb=kb)
    clssfy = classify_report(markup, kb=kb)

    return classrslts(context_document=markup,
                      exam_type="ctpa", 
                      report_text=report, 
                      classification_result=clssfy)


######################################################################################
# Multiple Report Functions (wrappers for convenience)
######################################################################################


def mark_reports(reports,kb=None,result_field=None,report_field=None):
    '''mark_reports is a convenience wrapper for mark_report
    :param reports: a table of reports, pandas data frame from load_reports
    :param kb: the knowledge base
    :param result_field: where to put the result. If none, will be placed in markup
    '''
    if report_field == None:
        report_field = 'report_text'
    logger.info("Marking %s reports, please wait...",reports.shape[0])
    result = reports.apply(lambda x: mark_report(x[report_field], 
                                                 kb=kb), 
                                                 axis=1)
    if result_field == None:
        result_field = "markup"
    reports[result_field] = result
    return reports


def analyze_reports(reports,kb=None,report_field=None,result_field=None):
    '''analyze_reports will apply the function analyze_report to the data frame
    of reports
    :param reports: the pandas data frame of reports from load_reports
    :param kb: the knowledge base
    :param report_field: the field in reports with the report text
    :param result_field: the field in reports to write the result to
    '''
    if report_field == None:
        report_field = "report_text"

    logger.info("Analyzing %s reports, please wait...",reports.shape[0])
    result = reports.apply(lambda x: analyze_report(x[report_field], 
                                                    kb=kb), 
                                                    axis=1)
    if result_field == None:
        result_field = "pe_result"
    
    reports[result_field] = result
    return reports


######################################################################################
# Report Label Transformation
######################################################################################


def label_remapping(reports,kb=None,result_field=None,drop_result=True):
    '''label_remapping will take the PEFinder result present in result_field
    and map it to a different schema.
    :param reports: the pandas data frame of reports from analyze_reports
    :param result_field: the result field where the result is present.
    :param drop_result: drop the raw result in favor of the remapping (default True)

    # study performed for PE? (LOOKING_FOR_PE_label)
    PE_STUDY == 1 and NONPESTUDY == 0

    # PE present: (PE_PRESENT_label)
    POSITIVE_PE == 1 and NEGATIVE_PE == 0 UNCERTAIN_PE = 2

    # Certainty (CERTAINTY_label)
    CERTAIN == 1, UNCERTAIN ==0

    # Acuity: (ACUITY_label)
    ACUTE == 1, CHRONIC == 0, MIXED == 2

    # Quality of the exam (QUALITY_label)
    DIAGNOSTIC == 1, NONDIAGNOSTIC == 2
    '''
    if kb == None:
        kb = load_knowledge_base()

    new_columns = ["PE_PRESENT_label","CERTAINTY_label","ACUITY_label",
                   "LOOKING_FOR_PE_label","ACUITY_label"]
    for new_column in new_columns:
        reports[new_column] = None

    # 1: ('AMBIVALENT', 
    # 'DISEASE_STATE == 2'),
    lookup = {1: {"PE_PRESENT_label":"UNCERTAIN_PE",
                  "CERTAINTY_label":"UNCERTAIN",
                  "ACUITY_label": None},

    # 2: ('Negative/Certain/Acute', 
    # 'DISEASE_STATE == 0 and CERTAINTY_STATE == 1')
              2 :{"PE_PRESENT_label":"NEGATIVE_PE",
                  "CERTAINTY_label":"CERTAIN",
                  "ACUITY_label":"ACUTE"},

    # 3: ('Negative/Uncertain/Chronic', 
    # 'DISEASE_STATE == 0 and CERTAINTY_STATE == 0 and ACUTE_STATE == 0'),
              3 :{"PE_PRESENT_label":"NEGATIVE_PE",
                  "CERTAINTY_label":"UNCERTAIN",
                  "ACUITY_label":"CHRONIC"},

    # 4: ('Positive/Uncertain/Chronic',
    #  'DISEASE_STATE == 1 and CERTAINTY_STATE == 0 and ACUTE_STATE == 0'),
              4 :{"PE_PRESENT_label":"POSITIVE_PE",
                  "CERTAINTY_label":"UNCERTAIN",
                  "ACUITY_label":"CHRONIC"},

    # 5: ('Positive/Certain/Chronic',
    #  'DISEASE_STATE == 1 and CERTAINTY_STATE == 1 and ACUTE_STATE == 0'),
              5 :{"PE_PRESENT_label":"POSITIVE_PE",
                  "CERTAINTY_label":"CERTAIN",
                  "ACUITY_label":"CHRONIC"},

    # 6: ('Negative/Uncertain/Acute',
    #  'DISEASE_STATE == 0 and CERTAINTY_STATE == 0'),
              6 :{"PE_PRESENT_label":"NEGATIVE_PE",
                  "CERTAINTY_label":"UNCERTAIN",
                  "ACUITY_label":"ACUTE"},

    # 7: ('Positive/Uncertain/Acute',
    #  'DISEASE_STATE == 1 and CERTAINTY_STATE == 0 and ACUTE_STATE == 1'),
              7 :{"PE_PRESENT_label":"POSITIVE_PE",
                  "CERTAINTY_label":"UNCERTAIN",
                  "ACUITY_label":"ACUTE"},

    # 8: ('Positive/Certain/Acute',
    #  'DISEASE_STATE == 1 and CERTAINTY_STATE == 1 and ACUTE_STATE == 1')}
              8 :{"PE_PRESENT_label":"POSITIVE_PE",
                  "CERTAINTY_label":"CERTAIN",
                  "ACUITY_label":"ACUTE"}
    } 

    missing = 0
    for row in reports.iterrows():
        res = row[1][result_field]
        if "pulmonary_embolism" in res.classification_result:
            classification = res.classification_result['pulmonary_embolism'][0]
            new_columns = list(lookup[classification].keys())
            new_values = list(lookup[classification].values())
            reports.loc[row[0],new_columns] = new_values
        else:
            missing +=1

    logger.warning(" % reports did not have a pulmonary embolism classification result!", missing)

    if drop_result == True:
        logger.info("Dropping column %s",result_field)
        reports = reports.drop(result_field, 1)
    return reports
