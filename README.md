# IBM Watson Assistant integration with MSK Engage database
### Introduction
This project produces a Watson Assistant that conversationalizes an MSK Engage form. Specifically, it can:
* Authenticate users by username/MRN
* Retrieve a list of user forms
* Dynamically generate Watson dialogue for a survey given a form alias
* Create uniquely ID'ed variables for answers, ready for future answer storage

You can view the final chatbot product [here](#https://web-chat.global.assistant.watson.cloud.ibm.com/preview.html?region=us-east&integrationID=e5b7ca42-456b-438d-9d02-da0b4b888313&serviceInstanceID=0e9aeb62-d6e3-4a52-b506-320af8459ed2). Be sure to refresh the page between forms.

### Forms used
This project used MSK's "covid_screen" [(Novel Coronavirus (COVID‑19) Screening Questionnaire)](#http://engage.mskcc.org/questionnaires/Novel_Coronavirus_(COVID-19)_Screening_Questionnaire) and "bsa" [(Brief Symptom Assessment)](#http://engage.mskcc.org/questionnaires/Brief_Symptom_Assessment/ESAS) forms as a proof of concept.

"covid_screen" is a brief, 3 question, yes/no form.
"bsa" is a longer form with slider and yes/no questions.