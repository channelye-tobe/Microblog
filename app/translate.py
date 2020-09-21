#!flask/bin/python

#coding: utf-8

# This simple app uses the '/translate' resource to translate text from
# one language to another.

# This sample runs on Python 2.7.x and Python 3.x.
# You may need to install requests and uuid.
# Run: pip install requests uuid

#import os, sys

#parentdir = os.path.dirname(os.path.abspath(__file__))
#sys.path.append('parentdir')

import os, requests, uuid, json
from config import TRANSLATOR_TEXT_SUBSCRIPTION_KEY, TRANSLATOR_TEXT_ENDPOINT, TRANSLATOR_TEXT_SUBSCRIPTION_REGION

subscription_key = TRANSLATOR_TEXT_SUBSCRIPTION_KEY
subscription_region = TRANSLATOR_TEXT_SUBSCRIPTION_REGION
endpoint = TRANSLATOR_TEXT_ENDPOINT

# If you encounter any issues with the base_url or path, make sure
# that you are using the latest endpoint: https://docs.microsoft.com/azure/cognitive-services/translator/reference/v3-0-translate

def microsoft_translate(text, destlange):
    path = '/translate?api-version=3.0'
    params = '&to=' + destlange
    constructed_url = endpoint + path + params

    headers = {
        'Ocp-Apim-Subscription-Key': subscription_key,
        'Ocp-Apim-Subscription-Region': subscription_region,
        'Content-type': 'application/json',
        'X-ClientTraceId': str(uuid.uuid4())
    }

    # You can pass more than one object in body.
    body = [{
        'text' : text
    }]
    request = requests.post(constructed_url, headers=headers, json=body)
    response = request.json()
    
    # print(json.dumps(response, sort_keys=True, indent=4, separators=(',', ': ')))
    #print(response)
    return(response[0]["translations"][0]["text"])
