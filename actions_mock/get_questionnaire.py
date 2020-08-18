import json
import ibm_boto3
from ibm_botocore.client import Config, ClientError

from actions_mock.get_user_forms import forms

# Connects to IBM dummy database
COS_BUCKET_NAME = 'watson-env-cos-standard-h48'
COS_ENDPOINT = "https://s3.us-east.cloud-object-storage.appdomain.cloud"
COS_API_KEY_ID = "jj8HGjytlf2Prmr4tvdcSyF5Nc6hvwor8ia3J4toSJT1"
COS_INSTANCE_CRN = "crn:v1:bluemix:public:cloud-object-storage:global:a/7366a3e44a224fb39605db6828750ed3:ae21529b-e030-4e9d-88a9-e3d89dcd7ffe:bucket:watson-env-cos-standard-h48"
COS_AUTH_ENDPOINT = "https://iam.cloud.ibm.com/identity/token"

cos = ibm_boto3.resource(
    "s3",
    ibm_api_key_id=COS_API_KEY_ID,
    ibm_service_instance_id=COS_INSTANCE_CRN,
    ibm_auth_endpoint=COS_AUTH_ENDPOINT,
    config=Config(signature_version="oauth"),
    endpoint_url=COS_ENDPOINT
)


def main(params):

    form_info = next(f for f in forms if f['alias'] == params['alias'])

    return {
        'alias': params['alias'],
        'id': form_info['id'],
        'name': form_info['name'],
        'nodes': json.loads(get_item(f"form_{params['alias']}"))
    }


def get_item(item_name):
    print(f"Retrieving item from bucket: {COS_BUCKET_NAME}, key: {item_name}")
    try:
        file = cos.Object(COS_BUCKET_NAME, item_name).get()
        return file["Body"].read()
    except ClientError as be:
        print(f"CLIENT ERROR: {be}\n")
    except Exception as e:
        print(f"Unable to retrieve file contents: {e}")
