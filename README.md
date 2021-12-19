# Text Alert Google Cloud Function using Twilio API

[![Build Status](https://travis-ci.org/nslocomotives/text_alert_function.svg?branch=main)](https://travis-ci.org/nslocomotives/text_alert_function)
![GitHub](https://img.shields.io/github/license/nslocomotives/text_alert_function)
![code compliance workflow](https://github.com/nslocomotives/text_alert_function/workflows/code%20compliance%20workflow/badge.svg?branch=main)

A [Google Cloud Function](https://cloud.google.com/functions/) that sends a message and a list of mobile numbers to [Twilio API](https://www.twilio.com/docs/usage/api).

## Example format of how the function is called by the Google cloud message queue using base64 encoding

This will need to be bas 64 encoded I would use a site such as: https://www.base64encode.org/ and past the following into the encode field, dont forget to change the mobile nuber to the number you wish to recive the text from...

``{"alert":"Something happened!","recipiants":["+4412345678","+4423456789"]}``

Then copy the encoded value and wrap it with the data variable name in json you should end up with something like this... (this is using the above phone numbers)

``{"data":"eyJhbGVydCI6IlNvbWV0aGluZyBoYXBwZW5lZCEiLCJyZWNpcGlhbnRzIjpbIis0NDEyMzQ1Njc4IiwiKzQ0MjM0NTY3ODkiXX0="}``

paste this into the testing field for the google cloud function and then hit the test, you should then get some usefull logging. 

## Deploy

### Twilo
  * Setup a Twilio account if you don't have one please use my referral link here: [www.twilio.com](www.twilio.com/referral/OBoqCY)
  * Get your ACCOUNT SID, API Key & generate a Token: https://www.twilio.com/console

### Google Cloud Functions
  * If you've never used gcloud or deployed a Cloud Function before, run through the [Quickstart](https://cloud.google.com/functions/docs/quickstart#functions-update-install-gcloud-node8) to make sure you have a GCP project with the Cloud Functions API enabled before proceeding.

  * Create and populate the secrets in Google Cloud [Quickstart](https://cloud.google.com/secret-manager/docs/quickstart).  I would advise just adding them in the console for Google Cloud [secrets Manager](https://console.cloud.google.com/security/secret-manager), you will have to enable the API and then you are free to create the required secrets with the values from Twilio console.  

  | secret name | Value |Notes|
  |:------------|:------|:----|
  |TWILIO_FROM  |``<mobile number>``| You will need to purchase a number to use and set it up|
  |TWILIO_AUTH_TOKEN|``<AUTH TOKEN>``| Available from the Twilio dashboard usually hidden|
  |TWILIO_ACCOUNT_SID|``<ACCOUNT SID>``| Available also from the Twilio Dashboard|


  * Fork/clone this repo
  * Within the repo, deploy this cloud function with:

  ```console
  $ gcloud functions deploy textalert \
  --trigger-token=textAlert \
  --runtime=python37 \
  --source=. \
  --project $(gcloud config list --format 'value(core.project)')
  ```


## Testing

### Prerequisites
* python37
* pytest
* pylint

### Unit tests
```console
$ pip install pytest pylint
$ pytest
$ pylint main.py
```

### Ad-hoc tests

```
To be done...
```

## Contributing
Contributions welcome! Please see [CONTRIBUTING.md](docs/CONTRIBUTING.md).

## License
This project is released under the ISC license, which can be found in [LICENSE](LICENSE).

## References
* Google Cloud Functions
  * [Pub\Sub Triggers](https://cloud.google.com/functions/docs/calling/pubsub)
  * [Using Secrets](https://cloud.google.com/secret-manager/docs/creating-and-accessing-secrets#secretmanager-create-secret-python)
  * [Testing Background Functions](https://cloud.google.com/functions/docs/testing/test-background)
  * [Testing and CI/CD](https://cloud.google.com/functions/docs/bestpractices/testing)
* Twilio
  * [Twilio API Keys](https://www.twilio.com/console)
  * [Quickstart with Python](https://www.twilio.com/docs/sms/quickstart/pythons)
  * [Twilio Automatic Testing](https://www.twilio.com/docs/sms/tutorials/automate-testing)
