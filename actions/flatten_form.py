# This script turns Zach Rachlin's API output into a digestible & labeled list to be used in "create_dialog"

from contextlib import contextmanager
from random import randint


def main(params):
    # Converts a tree-like MSK Engage questionnaire
    # into a list of text and question nodes

    nodes = params['nodes']
    dialog_nodes = []

    def append_node(node: dict) -> None:
        node_type = node['elementType']

        if node_type == 'PageBreakElement':
            pass

        elif node_type == 'QuestionSurveyElement':
            dialog_nodes.append({
                'type': 'question',
                'text': node['English']['Text'],
                'alias': node['English']['QuestionAnswerAlias'],
                'options': []
            })

        elif node_type == 'AnswerSurveyElement':
            if 'English' in node:
                # For "slider" type questions, our solution was to list all option values 1-10 as possible answers, and
                # change the question to include the scale metrics ("good"/"bad")
                if 'slider' in node['English']['QuestionAnswerAlias']:
                    dialog_nodes[-1]['text'] += f" Where 0 is {node['English']['MinSliderAnswer']} and 10 {node['English']['MaxSliderAnswer']}"
                    dialog_nodes[-1]['options'] = [
                        {
                            'text': str(i),
                            'alias': f"option_{i}",
                            'id': ''
                        }
                        for i in range(11)
                    ]
                else:
                    dialog_nodes[-1]['options'].append({
                        'text': node['English']['Text'],
                        'alias': node['English']['QuestionAnswerAlias'],
                        'id': get_answer_id(
                            question_alias=dialog_nodes[-1]['alias'],
                            answer_alias=node['English']['QuestionAnswerAlias']
                        )
                    })

        elif node_type == 'SectionSurveyElement':
            dialog_nodes.append({
                'type': 'text',
                'text': f"Section. {node['English']['Text']}"
            })

        elif node_type == 'TextBlockSurveyElement':
            text = node['English']['Text']

            if nodes[str(node['parentId'])]['elementType'] == 'Alert':
                text = f'Alert. {text}'

            dialog_nodes.append({
                'type': 'text',
                'text': text
            })

        # Recursively retrieves children nodes
        if 'children' in node:
            for node_id in node['children']:
                append_node(nodes[str(node_id)])

    for node_id in nodes['0']['children']:
        append_node(nodes[str(node_id)])

    return {
        'alias': params['alias'],
        'name': params['name'],
        'id': params['id'],
        'dialog_nodes': dialog_nodes
    }

# Retrieves real question_alias and answer_alias from Engage database, in preparation for storing answers in specific
# locations in the database. In the "Mock" version, this function calls our hard-coded dummy IBM database.
def get_answer_id(question_alias, answer_alias):
    try:
        query = """
            SELECT A.Id answer_id FROM Question Q
                JOIN Answer A on Q.Id = A.QuestionId
            WHERE Q.Alias = ?
                AND Q.ValidTo IS NULL
                AND A.Alias = ?
        """

        return exec_and_get_row_dicts(query, parameters=(question_alias, answer_alias))[0]['answer_id']

    except:
        return randint(0, 1000)


@contextmanager
def get_cursor():
    import os
    import pyodbc

    conn = pyodbc.connect(
        server='SMSKTSQLEGAO',
        database='DMSKTEFORMS',
        user=f"MSKCC\{os.getenv('LDAP_USERNAME')}",
        password=os.getenv('LDAP_PASSWORD'),
        tds_version='7.3',
        port=52421,
        driver='/usr/local/lib/libtdsodbc.so'       # Windows users may run into trouble with this library
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
