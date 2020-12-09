"""This script is google cloud function that listens on a topic
and sends a text alert based on the payload passed to it in json)"""

import base64
import inspect
import logging
import logging.handlers
from decouple import config
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
from google.cloud import secretmanager

#setting up loggers
logger = logging.getLogger('textAlert')
logger.setLevel(logging.DEBUG)

fh = logging.handlers.RotatingFileHandler(
    config(
        'LOGGING_LOCATION',
        default='/var/log/textalert.log'
        ),
    maxBytes=10240,
    backupCount=5
    )
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

def send_text(recipiant, payload):
    """ the fuction to send data to the twillio API in order to deliver the text message """
    message = {}
    client = Client(payload['account_sid'], payload['auth_token'])
    try:
        message = client.messages.create(
                                    from_=payload['from'],
                                    body=payload['alert'],
                                    to=recipiant
                                    )
        if inspect.isclass(message) is True:
            logger.info(message.sid)
    except TwilioRestException as error:
        logger.debug(
            'Exeption thrown HTTP %s error : %s | for more info %s ',
            error.status,
            error.msg,
            error.uri
            )
        message = {
            'uri' : error.uri,
            'status' : error.status,
            'msg' : error.msg,
            'code' : error.code,
            'method' : error.method,
            'details' : error.details,
            'error' : 'Text not sent',
            'recipiant': recipiant
            }
        logger.error(message['code'])
        logger.error(message['error'])
    return message

def unpack_data():
    """Function to unpack data from its encoded form"""
    result = ""
    return result

def build_payload(alert):
    """Function to build payload to pass to twilio"""
    payload = {}
    payload['alert'] = alert
    payload['account_sid'] = get_secret('TWILIO_ACCOUNT_SID')
    payload['auth_token'] = get_secret('TWILIO_AUTH_TOKEN')
    payload['from'] = get_secret('TWILIO_FROM')
    return payload


def textalert(event, context):
    """Fucntion called by google cloud message """
    if 'data' in event:
        data = base64.b64decode(event['data']).decode('utf-8')
        # TODO: what is this eval doing?  there should be a better way to do this in python. # pylint: disable=W0511
        data = eval(data) # pylint: disable=W0123
    else:
        data = False
        # TODO: add something here to exit gracefully from the function # pylint: disable=W0511
        # with a nice log to indicate the fix

    logger.info(" [x] Received %s | %s", data, context)
    recipiants = data['recipiants']
    payload = build_payload(data['alert'])
    for recipiant in recipiants:
        logger.info('texting %s : %s', recipiant, payload['alert'])
        result = send_text(recipiant, payload)
        logger.debug(result)
    logger.info(" [x] Done")
