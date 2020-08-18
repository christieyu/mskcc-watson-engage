# This script does the grunt work of generating Watson dialog nodes from a flattened form from Zach Rachlin's API

import logging

from ibm_watson import AssistantV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator

# we connect to our assistant skill, "Engage Forms Test"
ASSISTANT_URL = 'https://api.us-east.assistant.watson.cloud.ibm.com/'
ASSISTANT_ID = 'd3351a43-ecee-4dce-a771-774ff604308a'
ASSISTANT_API_KEY = '819Rh64snIJPiQ0mEbTGR_eIYzXhYvZsd_aE0VCTYeLb'
ASSISTANT_WORKSPACE_ID = 'dc2fde36-35cd-43f0-8acd-4676da8add59'

authenticator = IAMAuthenticator(
    apikey=ASSISTANT_API_KEY
)
assistant = AssistantV1(
    version='2020-04-01',
    authenticator=authenticator
)

assistant.set_service_url(ASSISTANT_URL)


def main(params):
    # Creates the dialog in Watson assistant
    # using the API

    alias = params['alias']
    dialog_nodes = params['dialog_nodes']

    try:
        delete_form(alias=alias)
    except Exception as e:
        logging.error(e)

    # if we are loading a brand new form
    create_form(params)

    for i, (previous, current) in enumerate(zip(dialog_nodes, dialog_nodes[1:])):

        if i == 0:
            create_fn = create_text if previous['type'] == 'text' else create_question
            create_fn(index=i, dialog_node=previous, form_alias=alias)
            link_nodes(source=f'form_{alias}', target=f'form_{alias}_0')

        create_fn = create_text if current['type'] == 'text' else create_question
        create_fn(index=i + 1, dialog_node=current, form_alias=alias)
        link_nodes(f'form_{alias}_{i}', f'form_{alias}_{i + 1}')

# before updating the form nodes, we need to delete the old nodes
def delete_form(alias):
    return assistant.delete_dialog_node(
        workspace_id=ASSISTANT_WORKSPACE_ID,
        dialog_node=f'form_{alias}'
    )


def create_form(form):
    # Create the root node of the form.
    # Sections of the form are children of this node

    # Add form to the @forms entity in Watson
    # and use the form id as a synonym for this entity
    try:
        assistant.create_value(
            workspace_id=ASSISTANT_WORKSPACE_ID,
            entity='forms',
            value=form['alias'],
            synonyms=[form['id'],]
        )
    except Exception as e:
        logging.error(e)

    assistant.create_dialog_node(
        workspace_id=ASSISTANT_WORKSPACE_ID,
        dialog_node=f"form_{form['alias']}",
        parent='node_3_1596555609144',
        conditions=f"@forms:{form['alias']}",
        output=text_output(form['name']),
        disambiguation_opt_out=True
    )

# for the text portions of the form
def text_output(text):
    return {
        'generic': [
            {
                'response_type': 'text',
                'selection_policy': 'sequential',
                'values': [
                    {
                        'text': text
                    }
                ]
            }
        ]
    }

# for answer options to questions. Answers option values are ID'ed as {question_alias}_{option_alias} as recorded in
# the Engage SQL database, not Zach Rachlin's API
def options_output(text, question_alias, options):
    return {
        'generic': [
            {
                'response_type': 'option',
                'title': text,
                'options': [
                    {
                        'label': option['text'],
                        'value': {
                            'input': {'text': f"{question_alias}_{option['alias']}"}
                        }
                    } for option in options
                ]
            }
        ]
    }


def get_forms_folder_id() -> str:
    return \
        next(dn for dn in
             assistant.list_dialog_nodes(ASSISTANT_WORKSPACE_ID, page_limit=1000).get_result()['dialog_nodes']
             if dn['type'] == 'folder' and dn['title'] == 'Forms')['dialog_node']


def create_text(index, dialog_node, form_alias):
    # Create one basic text node that maps to one
    # text blob from the original questionnaire
    assistant.create_dialog_node(
        workspace_id=ASSISTANT_WORKSPACE_ID,
        dialog_node=f'form_{form_alias}_{index}',
        parent=f'form_{form_alias}',
        output=text_output(dialog_node['text']),
        disambiguation_opt_out=True
    )

# for question text
def create_question(index, dialog_node, form_alias):
    # TODO Map different types of options

    try:
        assistant.delete_entity(
            workspace_id=ASSISTANT_WORKSPACE_ID,
            entity=dialog_node['alias']
        )
    except:
        pass

# Here we create entities, alias = "question_alias" and values = all possible "answer_alias"es
# We do this as verification that the user has selected an answer only from the possible answer pool for each question
# It is cumbersome and a work-around for Watson's non-linear entity recognition flow
    assistant.create_entity(
        workspace_id=ASSISTANT_WORKSPACE_ID,
        entity=dialog_node['alias'],
    )

    for option in dialog_node['options']:
        assistant.create_value(
            workspace_id=ASSISTANT_WORKSPACE_ID,
            entity=dialog_node['alias'],
            value=f"{dialog_node['alias']}_{option['alias']}",
        )

    # Create the question main node and
    # configure the webhook
    assistant.create_dialog_node(
        workspace_id=ASSISTANT_WORKSPACE_ID,
        dialog_node=f'form_{form_alias}_{index}',
        type='frame',
        parent=f'form_{form_alias}',
        title=dialog_node['alias'].lower(),
        actions=[
            {
                'name': 'main_webhook',
                'type': 'webhook',
                'parameters': {
                    'action': f'store_response',
                    'assessment_id': '189203',
                    'answer_id': '1289347'
                },
                'result_variable': 'webhook_result'
            }
        ],
        disambiguation_opt_out=True
    )

    # Response when the webhook returns successfully
    assistant.create_dialog_node(
        workspace_id=ASSISTANT_WORKSPACE_ID,
        dialog_node=f'form_{form_alias}_{index}_webhook_response',
        type='response_condition',
        parent=f'form_{form_alias}_{index}',
        conditions='$webhook_result'
    )

    # Slot to persist the user response
    assistant.create_dialog_node(
        workspace_id=ASSISTANT_WORKSPACE_ID,
        dialog_node=f'form_{form_alias}_{index}_slot',
        type='slot',
        parent=f'form_{form_alias}_{index}',
        variable=f'$form_{form_alias}_{index}'
    )

    # Event handler that displays the question
    # and lists the options
    assistant.create_dialog_node(
        workspace_id=ASSISTANT_WORKSPACE_ID,
        dialog_node=f'form_{form_alias}_{index}_text',
        type='event_handler',
        parent=f'form_{form_alias}_{index}_slot',
        event_name='focus',
        output=options_output(dialog_node['text'], dialog_node['alias'], dialog_node['options'])
    )

    # Handler to specify when the user input is stored
    assistant.create_dialog_node(
        workspace_id=ASSISTANT_WORKSPACE_ID,
        dialog_node=f'form_{form_alias}_{index}_handler',
        type='event_handler',
        parent=f'form_{form_alias}_{index}_slot',
        event_name='input',
        context={
            f'form_{form_alias}_{index}': f"@{dialog_node['alias']}",
        },
        conditions=f"@{dialog_node['alias']}",
    )


def link_nodes(source, target):
    # Add a jump_to from one node to the other
    # and is used to link the nodes of the form
    return assistant.update_dialog_node(
        workspace_id=ASSISTANT_WORKSPACE_ID,
        dialog_node=source,
        new_next_step={
            'behavior': 'jump_to',
            'selector': 'body',
            'dialog_node': target
        }
    )
