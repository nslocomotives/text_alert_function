from decouple import config
from main import send_text, textalert

twilio_account_sid = config('TWILIO_ACCOUNT_SID')
twilio_auth_token = config('TWILIO_AUTH_TOKEN')
twilio_from = config('TWILIO_FROM')

def test_send_text_to_valid_phone_number() -> None:
    payload = {}
    payload['account_sid'] = twilio_account_sid
    payload['auth_token'] = twilio_auth_token
    payload['from'] = twilio_from
    payload['alert'] = 'hello I am an alert!'
    recipiant = "+15005550006"
    results = send_text(recipiant, payload)
    assert results.account_sid == twilio_account_sid

def test_send_text_to_invalid_phone_number() -> None:
    payload = {}
    payload['account_sid'] = twilio_account_sid
    payload['auth_token'] = twilio_auth_token
    payload['from'] = twilio_from
    payload['alert'] = 'hello I am an alert!'
    recipiant = "+15005550001"

    results = send_text(recipiant, payload)
    assert results['error'] == "Text not sent"

def test_send_text_unroutable_phone_number() -> None:
    '''testting for https://www.twilio.com/docs/api/errors/21612 '''
    payload = {}
    payload['account_sid'] = twilio_account_sid
    payload['auth_token'] = twilio_auth_token
    payload['from'] = twilio_from
    payload['alert'] = 'hello I am an alert!'
    recipiant = "+15005550002"

    results = send_text(recipiant, payload)
    assert results['error'] == "Text not sent"

def test_send_text_does_not_have_international_permisions() -> None:
    '''testting for https://www.twilio.com/docs/api/errors/21408 '''
    payload = {}
    payload['account_sid'] = twilio_account_sid
    payload['auth_token'] = twilio_auth_token
    payload['from'] = twilio_from
    payload['alert'] = 'hello I am an alert!'
    recipiant = "+15005550003"

    results = send_text(recipiant, payload)
    assert results['error'] == "Text not sent"

def test_send_text_blocked_phone_number_from_your_accnt() -> None:
    '''testting for https://www.twilio.com/docs/api/errors/21610 '''
    payload = {}
    payload['account_sid'] = twilio_account_sid
    payload['auth_token'] = twilio_auth_token
    payload['from'] = twilio_from
    payload['alert'] = 'hello I am an alert!'
    recipiant = "+15005550004"

    results = send_text(recipiant, payload)
    assert results['error'] == "Text not sent"

def test_send_text_number_incaperbale_of_receving_sms() -> None:
    '''testting for https://www.twilio.com/docs/api/errors/21614 '''
    payload = {}
    payload['account_sid'] = twilio_account_sid
    payload['auth_token'] = twilio_auth_token
    payload['from'] = twilio_from
    payload['alert'] = 'hello I am an alert!'
    recipiant = "+15005550009"

    results = send_text(recipiant, payload)
    assert results['error'] == "Text not sent"

def test_send_text_from_valid_phone_number() -> None:
    payload = {}
    payload['account_sid'] = twilio_account_sid
    payload['auth_token'] = twilio_auth_token
    payload['from'] = "+15005550006"
    payload['alert'] = 'hello I am an alert!'
    recipiant = "+15005550006"
    results = send_text(recipiant, payload)
    assert results.account_sid == twilio_account_sid

def test_send_text_from_invalid_phone_number() -> None:
    '''testing for https://www.twilio.com/docs/api/errors/21212 '''
    payload = {}
    payload['account_sid'] = twilio_account_sid
    payload['auth_token'] = twilio_auth_token
    payload['from'] = "+15005550001"
    payload['alert'] = 'hello I am an alert!'
    recipiant = "+15005550006"
    results = send_text(recipiant, payload)
    assert results['code'] == 21212
    assert results['error'] == "Text not sent"

def test_send_text_from_unowned_phone_number() -> None:
    '''testing for https://www.twilio.com/docs/api/errors/21606 '''
    payload = {}
    payload['account_sid'] = twilio_account_sid
    payload['auth_token'] = twilio_auth_token
    payload['from'] = "+15005550007"
    payload['alert'] = 'hello I am an alert!'
    recipiant = "+15005550006"
    results = send_text(recipiant, payload)
    assert results['code'] == 21606
    assert results['error'] == "Text not sent"

def test_send_text_from_phone_number_full_SMS_QUEUE() -> None:
    '''testing for https://www.twilio.com/docs/api/errors/21611 '''
    payload = {}
    payload['account_sid'] = twilio_account_sid
    payload['auth_token'] = twilio_auth_token
    payload['from'] = "+15005550008"
    payload['alert'] = 'hello I am an alert!'
    recipiant = "+15005550006"
    results = send_text(recipiant, payload)
    assert results['code'] == 21611
    assert results['error'] == "Text not sent"

def test_textalert_with_nodata() -> None:
    '''testing for clean exit with no data'''
    event = {}
    context = {}
    textalert(event, context) == r'No data passed in event consumed, please check the producer is sending event[\'data\'\]'
