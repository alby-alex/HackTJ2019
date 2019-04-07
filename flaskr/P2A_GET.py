import requests

import json

x_api_key = 'ie5EtNqb2pafUpw0FsMC84hHqrW9L4uf2Ql9YTJF'

endpoint = 'https://fmrrixuk32.execute-api.us-east-1.amazonaws.com/hacktj/legislators'


def getInfo(address):
    parameters = {
        'address':  address
    }
    headers = {
        'X-API-Key': x_api_key
    }
    dict = []
    response = requests.get(endpoint, params=parameters, headers=headers)

    representatives = json.loads(response.text)['officials']
    for representative in representatives:
        first_name = representative['first_name']
        last_name = representative['last_name']
        photo = representative['photo']
        temp = representative['socials']
        for x in temp:
            twitter_handle = x['identifier_type']
            if "TWITTER" == twitter_handle:
                twitter_handle = x['identifier_value']
                break
        levelC = representative['office_details']['district']['type']
        if('NATIONAL' in levelC):
            levelC = 'NATIONAL'
        else:
            levelC = 'STATE'
        dict.append({'Name' : (first_name + last_name), 'Photo' : photo, 'Twitter' : twitter_handle, 'Level' : levelC})
    return dict;


print(getInfo("6560 Braddock Rd"))
