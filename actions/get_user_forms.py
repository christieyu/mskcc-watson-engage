# This script runs a SQL query to find what forms a user needs to complete. Since this involves PHI, we replaced this
# in "actions_mock" with a hard-coded dict of forms to fill.

import os
from itertools import groupby
from contextlib import contextmanager

import pyodbc
import requests


def main(params):
    query = """
        SELECT Alias alias,
            Name name,
            CAST(AssignmentDate as date) assignment_date,
            a.Id assessment_id
        FROM Assessment a
            INNER JOIN PatientInfo pi ON pi.Id = a.PatientInfoId
            INNER JOIN Survey s ON s.SurveyConfigurationId = a.SurveyId
        WHERE a.StatusId = 1
            AND CAST(a.AssignmentDate AS DATE) <= CAST(Getdate() AS DATE)
            AND pi.MRN = ?
    """

    results = exec_and_get_row_dicts(query, parameters=(params['mrn'],))

    return [
        dict(id=get_form_id(alias=a), **max(s, key=lambda s: s['assessment_id']))
        for (a, s) in groupby(results, key=lambda f: f['alias'])
    ]


def get_form_id(alias):
    try:
        response = requests.get(f"http://engage.mskcc.org/api/questionnaires")

        response.raise_for_status()

        return next(n for n in response.json() if n['Alias'] == alias)['Id']
    except:
        return ''


@contextmanager
def get_cursor():
    conn = pyodbc.connect(
        server='SMSKTSQLEGAO',
        database='DMSKTEFORMS',
        user=f"MSKCC\{os.getenv('LDAP_USERNAME')}",
        password=os.getenv('LDAP_PASSWORD'),
        tds_version='7.3',
        port=52421,
        driver='/usr/local/lib/libtdsodbc.so'
    )
    cursor = conn.cursor()
    try:
        yield cursor
    finally:
        cursor.close()
        conn.close()


def exec_and_get_row_dicts(sql, parameters=None):
    with get_cursor() as cursor:
        cursor.execute(sql, parameters)

        result_set_description = cursor.description
        if result_set_description is not None:
            field_names = [field[0] for field in result_set_description]
            return [dict(list(zip(field_names, row))) for row in cursor.fetchall()]
        else:
            return None
