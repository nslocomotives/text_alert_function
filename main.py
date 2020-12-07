"""This script is google cloud function that listens on a topic
and sends a text alert based on the payload passed to it in json)"""

import base64
import logging
import logging.handlers
from decouple import config
from twilio.rest import Client
from google.cloud import secretmanager

#setting up loggers
logger = logging.getLogger('textAlert')
logger.setLevel(logging.INFO)

fh = logging.handlers.RotatingFileHandler(config('LOGGING_LOCATION'), maxBytes=10240, backupCount=5)
fh.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)

ch = logging.StreamHandler()
ch.setLevel(logging.WARNING)
ch.setFormatter(formatter)

logger.addHandler(fh)
logger.addHandler(ch)


def assign_secret_variable( secret_id, project_id=config('GCP_PROJECT'), version_id='latest'):
    """This funtion is used to fetch environement variables from google clouds seceret store"""
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"
        # Build the resource name of the secret version.
    name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"

    # Access the secret version.
    response = client.access_secret_version(request={"name": name})

    # Return the secret payload.
    #
    # WARNING: Do not print the secret in a production environment - this
    # function is to access the secret material.
    payload = response.payload.data.decode("UTF-8")
    return payload

def get_secret(secret_name):
    """ A wrapper for the secret variable assignement to perform a get"""
    response = assign_secret_variable(secret_name)
    return response

def send_text(recipiant, alert):
    """ the fuction to send data to the twilo API in order to deliver the text message """
    twilo_account_sid = get_secret('TWILO_ACCOUNT_SID')
    twilo_auth_token = get_secret('TWILO_AUTH_TOKEN')
    twilo_from = get_secret('TWILO_FROM')
    client = Client(twilo_account_sid, twilo_auth_token)

    message = client.messages.create(
                                from_=twilo_from,
                                body=alert,
                                to=recipiant
                                )
    logger.info(message.sid)


def textAlert(event, context):
    """Fucntion called by google cloud message """
    if 'data' in event:
        data = base64.b64decode(event['data']).decode('utf-8')
        # TODO: what is this eval doing?  there should be a better way to do this in python.
        data = eval(data)
    else:
        data = False

    logger.info(" [x] Received %s | %s", data, context)
    recipiants = data['recipiants']
    alert = data['alert']
    for recipiant in recipiants:
        logger.info('texting %s : %s', recipiant, alert)
        send_text(recipiant, alert)

    logger.info(" [x] Done")
