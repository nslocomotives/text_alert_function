import pika
import time
from decouple import config
import json
import logging
import logging.handlers
from twilio.rest import Client
from google.cloud import secretmanager


twilo_account_sid = getSecret('TWILO_ACCOUNT_SID')
twilo_auth_token = getSecret('TWILO_AUTH_TOKEN')
twilo_from = getSecret('TWILO_FROM')

client = Client(twilo_account_sid, twilo_auth_token)

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

sleepTime = 10
logger.info(' [*] Sleeping for %s seconds. ', sleepTime)
time.sleep(30)

logger.info(' [*] Connecting to server ...')
url = getSecret('RABBITMQ_AMQP_URL')
params = pika.URLParameters(url)
connection = pika.BlockingConnection(params)
channel = connection.channel()
channel.queue_declare(queue=config('RABBITMQ_TASK_QUEUE'), durable=True)

logger.info(' [*] Waiting for messages.')

def getSecret(secret_name):
    response = assign_secret_variable(secret_name)
    return response

def assign_secret_variables( secret_id, project_id=config('GCP_PROJECT'), version_id='latest'):
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
    return("Plaintext: {}".format(payload))


def send_text(recipiant, alert):
    message = client.messages.create(
                                from_=twilo_from,
                                body=alert,
                                to=recipiant
                                )
    logger.info(message.sid)


def callback(ch, method, properties, body):
    logger.info(" [x] Received %s" % body)
    data = body.decode()
    data = json.loads(data)
    recipiants = data['recipiants']
    alert = data['alert']
    for recipiant in recipiants:
        logger.info('texting %s : %s', recipiant, alert)
        send_text(recipiant, alert)

    logger.info(" [x] Done")

    ch.basic_ack(delivery_tag=method.delivery_tag)

def textAlert(event, context):
    print(event)
    print(context)


channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue=config('RABBITMQ_TASK_QUEUE'), on_message_callback=callback)
channel.start_consuming()
