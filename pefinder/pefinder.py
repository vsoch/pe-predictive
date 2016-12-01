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

logging.info("radnlp version %s",radnlp.__version__)

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
        kb = get_knowledge_base()

    markup = mark_report(report, kb=kb)
    clssfy = classify_report(markup, kb=kb)

    return classrslts(context_document=markup,
                      exam_type="ctpa", 
                      report_text=report, 
                      classification_result=clssfy)


######################################################################################
# Multiple Report Functions (wrappers for convenience)
######################################################################################


def mark_reports(reports,kb=None):
    '''mark_reports is a convenience wrapper for mark_report
    :param reports: a table of reports, pandas data frame from load_reports
    :param kb: the knowledge base
    '''

def classify_reports(markups, kb=None):
    '''classify_reports is a convenience wrapper for classify_report
    :param reports: a table of reports, pandas data frame from load_reports
    :param kb: the knowledge base
    '''

def analyze_reports(reports,kb=None,report_field=None):
    if report_field == None:
        report_field = "report_text"

    logger.info("Analyzing %s reports, please wait...",reports.shape[0])
    result = reports.apply(lambda x: analyze_report(x[report_field], 
                                                    kb=kb), 
                                                    axis=1)
    
    reports['pe_result'] = result
    return reports
