from random import randint, sample
from datetime import timedelta, datetime


forms = [
    {
        "alias": "covid_screen",
        "name": "Novel Coronavirus (COVID-19) Screening Questionnaire",
        "id": "68"
    },
    {
        "alias": "BSA",
        "name": "Brief Symptom Assessment",
        "id": "12"
    },
    {
        "alias": "gynclincare",
        "name": "Gynecologic Clinical Care",
        "id": "22"
    }
]


def main(params):
    return {
        "forms": [dict(
            assignment_date=str((datetime.today() - timedelta(days=randint(0, 7))).date()),
            assessment_id=randint(0, 1000),
            **f
        ) for f in sample(forms, randint(1, len(forms)))]
    }
