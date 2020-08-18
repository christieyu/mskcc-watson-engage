# Retrieves info from Zach Rachlin's API

import requests


def main(params):
    return dict(
        alias=params['alias'],
        nodes=get_nodes(params['alias']),
        **get_info(params['alias'])
    )


def get_info(alias):
    response = requests.get(f"http://engage.mskcc.org/api/questionnaires")

    response.raise_for_status()

    form_info = next(n for n in response.json() if n['Alias'] == alias)

    return {
        'id': str(form_info['Id']),
        'name': form_info['Name']
    }


def get_nodes(alias):
    response = requests.get(
        f"http://engage.mskcc.org/api/questionnaires/search?searchTerm={alias}&searchMethod=alias")

    response.raise_for_status()

    return response.json()
