"""
Search GDC data via TCGA api.
"""
import os
import re
import json
import requests
import pandas as pd
import subprocess
from urllib.parse import urljoin

from .utils import edit_json, dir_check
from .checking import *


class ParamConstructor:
    param_mapping = {
            'projects': 'cases.project.project_id',
            'data_category': 'files.data_category',
            'data_type': 'files.data_type',
            'workflow_type': 'files.analysis.workflow_type',
            'file_type': 'files.file_type',
            'experimental_strategy': 'files.experimental_strategy',
            'platform': 'files.platform',
            'data_format': 'files.data_format',
            }

    def __init__(self,
                 projects,
                 data_category=None,
                 data_type=None,
                 workflow_type=None,
                 file_type=None,
                 sample_type=None,
                 experimental_strategy=None,
                 platform=None,
                 barcode=None,
                 access=None,
                 legacy=False
                 ):
        self.valid_param = {}

        if not isinstance(projects, list):
            projects = [projects]
        project_check(projects)
        self.projects = projects

        data_categories_check(projects, data_category)
        if data_category == 'Clinical':
            self.valid_param['data_type'] = 'Clinical Supplement'
            self.valid_param['data_format'] = 'BCR XML'
        self.valid_param['data_category'] = data_category
        self.data_category = data_category

        if data_type is not None:
            data_type_check(data_type)
            self.valid_param['data_type'] = data_type

        if workflow_type is not None:
            self.valid_param['workflow_type'] = workflow_type
        if file_type is not None:
            self.valid_param['file_type'] = file_type
        if sample_type is not None:
            self.valid_param['sample_type'] = sample_type
        if experimental_strategy is not None:
            self.valid_param['experimental_strategy'] = experimental_strategy
        if platform is not None:
            self.valid_param['platform'] = platform

        self.barcode = barcode
        self.access = access
        self.legacy = legacy

    def field_set(self):
        if self.data_category == 'Protein expression' and self.legacy:
            return {
                    'fields': 'archive.revision, archive.file_name, md5sum, state, \
                               data_category, file_id, platform, file_name, file_size, \
                               md5sum, submitter_id, data_type',
                    'expand': 'cases.samples.portions, cases.project, center, analysis'
                    }
        elif self.data_category in ['Clinical', 'Biospecimen']:
            return {
                    'expand': 'cases, cases.project, center, analysis'
                    }
        else:
            return {
                    #'expand': 'cases.samples.portions.analytes.aliquots, cases.project, \
                    #           center, analysis, cases.samples'
                    'expand': 'cases.project, center, analysis, cases.samples'
                    }
        
    def add_filter(self, field, value):
        content = {
                'op': 'in',
                'content': {
                    'field': field,
                    'value': [value]
                    }
                }
        return content

    def query(self, proj):
        baseURL = 'https://api.gdc.cancer.gov/files/'
        legacyURL = 'https://api.gdc.cancer.gov/legacy/files/'
        URL = legacyURL if self.legacy else baseURL

        filters = {'op': 'and',
                   'content': []
                   }
        cont_proj = self.add_filter(self.param_mapping.get('projects'), proj)
        filters['content'].append(cont_proj)

        for field, value in self.valid_param.items():
            content = self.add_filter(self.param_mapping.get(field), value)
            filters['content'].append(content)

        size = get_target_nb(proj, self.data_category, item='file_count')
        params = {
                'filters': json.dumps(filters),
                'format': 'JSON',
                'size': 2
                }
        print(json.dumps(params, indent=2))
        params.update(self.field_set())
        response = requests.post(URL, headers = {"Content-Type": "application/json"}, json=params)
        return response

    def form_response(self):
        self.result = pd.DataFrame()

        for proj in self.projects:
            response = self.query(proj)
            res_json = response.json()
            print(json.dumps(res_json,indent=2))
            hits = res_json['data']['hits']
            edit_json(hits, 'acl', None)
            edit_json(hits, 'project', proj)
        
            self.result = self.result.append(pd.DataFrame(hits))



def download(query, directory='GDCdata', method='client'):
    gdc_tool = './libs/bin/gdc-client'
    manifest = manifest_gensis(query, query.projects[0], directory)
    print('===================================================')
    path = os.path.join(directory, re.sub('\s', '_', query.data_category))
    dir_check(path)
    print(path)
    try:
        subprocess.run([
            gdc_tool,
            'download', 
            '-m', manifest,
            '-d', path
            ])
    except Exception:
        pass

def manifest_gensis(query, proj, path):
    dir_check(path)
    manifest = os.path.join(path, f'gdc_{proj}.manifest.txt')
    keys = ['file_id', 'file_name', 'md5sum', 'file_size', 'state']
    #dm = [content.get(key, '') for key in keys for content in query.result['data']['hits']]
    df = query.result[keys]
    df.columns = ['id', 'file_name', 'md5sum', 'file_size', 'state']
    df.to_csv(manifest, sep='\t', index=False)
    return manifest




