import requests

ip_lists = ['server1']

dict_to_send = {'value': 5}
response = requests.post('http://server1:8080/', json = dict_to_send)

print('response: ' + response.text)

response = requests.post('http://server2:8080/', json = dict_to_send)

print('response: ' + response.text)

while True:
    pass