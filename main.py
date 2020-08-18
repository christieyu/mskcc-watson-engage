# main(iu), main(guf), and main(lf) handle the main functions of this program

# The first line imports python scripts for real Engage-Watson integration. This pulls questionnaire info from
# Zach Rachlin's API, which is behind the firewall, as well as the MSK Engage database, which has real PHI.
# For security reasons, we have included a "actions_mock" import which takes functions that refer to "dummy data"
# located on IBM databases. By default, the "actions_mock" imports replace the first line of imports, unless
# commented out. Future engineers can comment out the second line with approval for real Engage-Watson integration.

from actions import identify_user, get_user_forms, create_dialog, flatten_form, get_questionnaire
from actions_mock import identify_user, get_user_forms, get_questionnaire


def load_form(params):
    create_dialog.main(flatten_form.main(get_questionnaire.main(params)))


def main(params):
    return {
        'identify_user': identify_user.main,
        'get_user_forms': get_user_forms.main,
        'load_form': load_form
    }.get(params['action'])(params)


if __name__ == '__main__':
    iu = {
        'action': 'identify_user',
        'username': 'doddsr'
    }

    guf = {
        'action': 'get_user_forms',
        'username': 'doddsr'
    }

    lf = {
        'action': 'load_form',
        'alias': 'covid_screen'
    }

    res = main(iu)

    print(res)
