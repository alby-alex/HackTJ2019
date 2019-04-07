import requests

import json

x_api_key = 'ie5EtNqb2pafUpw0FsMC84hHqrW9L4uf2Ql9YTJF'

endpoint = 'https://fmrrixuk32.execute-api.us-east-1.amazonaws.com/hacktj/legislators'
parameters = {
    'address': '6560 Braddock Rd'
}
headers = {
'X-API-Key': x_api_key
}

def getTwitterHandle(name):
    dict = {}
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
        dict[first_name + " " + last_name] = {'Photo' : photo, 'Twitter' : twitter_handle, 'Level' : levelC}
        #print('Your Representative in national Congress is ' + first_name + ' ' + last_name + ' ' + photo + ' ' + twitter_handle + ' ' + levelC)
    for x in dict:
        if(name in x):
            return dict.get(x).get('Twitter')