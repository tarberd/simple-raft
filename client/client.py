import requests

server_list = [
    'http://alce:8080/',
    'http://baleia:8080/',
    'http://camelo:8080/',
    'http://doninha:8080/'
]

dict_to_send = {'value': 5}

for server_url in server_list:
    print('send post to: ' + server_url)
    response = requests.post(server_url, json = dict_to_send)
    print('response: ' + response.text)
