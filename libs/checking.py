"""
params checking module.
"""

import os
import json
import requests
from urllib.parse import urljoin

from .errors import InputError


def gdc_status_check():
    response = requests.get('https://api.gdc.cancer.gov/status')
    return json.dumps(response.json(), indent=2)

def project_check(projects):
    valid_projects = get_gdc_projects()
    if not projects:
        raise Exception('Please set a valid project param')
    
    for proj in projects:
        if proj not in valid_projects:
            raise Exception('Please set a valid project param.')

def data_type_check(data_type):
    harmonized_data_type = ["Gene Expression Quantification",
                 "Copy Number Segment",
                 "Masked Copy Number Segment",
                 "Isoform Expression Quantification",
                 "miRNA Expression Quantification",
                 "Biospecimen Supplement",
                 "Gene Level Copy Number Scores",
                 "Clinical Supplement",
                 "Masked Somatic Mutation"
                 ]
    if data_type not in harmonized_data_type:
        raise InputError('Please set a valid data type param')

def data_categories_check(projects, data_category, legacy=False):
    for proj in projects:
        summary = get_project_summary(proj, legacy)
        valid_category = [item.get('data_category') for item in summary]
        print(valid_category)
        if not data_category:
            raise InputError('Please set a valid data category')
        if data_category not in valid_category:
            raise InputError('Please set a valid data category')

def get_project_summary(project, legacy=False):
    baseURL = 'https://api.gdc.cancer.gov/legacy/projects/' if legacy else \
            'https://api.gdc.cancer.gov/projects/'
    url = urljoin(baseURL, project)
    response = requests.get(url, params={'expand': 'summary,summary.data_categories', 'pretty':'true'})
    return response.json()['data']['summary']['data_categories']

def get_target_nb(project, data_category, legacy=False, item='case_count'):
    summary = get_project_summary(project)
    found = category_match(summary, data_category)
    return found.get('case_count')

def category_match(summary, category):
    try:
        for d in summary:
            if d.get('data_category', '') == category:
                return d
    except Exception:
        return None

def get_gdc_projects():
    ret = requests.get("https://api.gdc.cancer.gov/projects?size=1000&format=json")
    return [item['project_id'] for item in ret.json()['data']['hits']]



if __name__ == '__main__':
    summary = get_project_summary('TCGA-BRCA')
