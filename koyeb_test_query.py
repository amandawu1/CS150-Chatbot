import requests

data = {"query":"tell me about tufts"}
response = requests.post("https://replace_with_your_web_server_link", json=data)
print(response.text)
