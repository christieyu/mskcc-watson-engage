# From a unique MRN input, we can retrieve users' first name, last name, birthdate, and email

import os
from contextlib import contextmanager

import pyodbc


def main(params):
    query = """
            SELECT FirstName first_name,
                LastName last_name,
                CAST(BirthDate AS DATE) dob,
                EMail email
            FROM PatientInfo
            WHERE MRN = ?
        """

    return exec_and_get_row_dicts(query, parameters=(params['mrn'],))[0]


@contextmanager
def get_cursor():
    conn = pyodbc.connect(
        server='SMSKTSQLEGAO',
        database='DMSKTEFORMS',
        user=f"MSKCC\{os.getenv('LDAP_USERNAME')}",
        password=os.getenv('LDAP_PASSWORD'),
        tds_version='7.3',
        port=52421,
        driver='/usr/local/lib/libtdsodbc.so'   # Windows users may run into trouble with locating this library
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
