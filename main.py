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

def getSecret(secret_name):
    response = assign_secret_variable(secret_name)
    return response

def send_text(recipiant, alert):
    twilo_account_sid = getSecret('TWILO_ACCOUNT_SID')
    twilo_auth_token = getSecret('TWILO_AUTH_TOKEN')
    twilo_from = getSecret('TWILO_FROM')
    client = Client(twilo_account_sid, twilo_auth_token)

    message = client.messages.create(
                                from_=twilo_from,
                                body=alert,
                                to=recipiant
                                )
    logger.info(message.sid)


def textAlert(event, context):

    if 'data' in event:
        data = base64.b64decode(event['data']).decode('utf-8')
        data = eval(data)
    else:
        data = False

    logger.info(" [x] Received %s" % data)
    recipiants = data['recipiants']
    alert = data['alert']
    for recipiant in recipiants:
        logger.info('texting %s : %s', recipiant, alert)
        send_text(recipiant, alert)

    logger.info(" [x] Done")
