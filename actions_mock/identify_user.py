# Upon given a username, this function returns the user's MRN.

users = {
    'yuc2': {
        'first_name': 'Christie',
        'last_name': 'Yu',
        'email': 'yuc2@mskcc.org',
    },
    'doddsr': {
        'first_name': 'Ricardo',
        'last_name': 'Dodds',
        'email': 'doddsr@mskcc.org',
    },
    'gaitondd': {
        'first_name': 'Divya',
        'last_name': 'Gaitonde',
        'email': 'gaitondd@mskcc.org',
    }
}


def main(params):
    return users[params['mrn']]
