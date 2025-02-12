import os
import json
import requests
from requests_toolbelt.multipart.encoder import MultipartEncoder

# Read proxy config from environment
end_point = os.environ.get("proxy_endpoint")
api_key = os.environ.get("api_key")

def generate(
	model: str,
	system: str,
	query: str,
	temperature: float | None = None,
	lastk: int | None = None,
	session_id: str | None = None,
    rag_threshold: float | None = 0.5,
    rag_usage: bool | None = False,
    rag_k: int | None = None
	):
	

    headers = {
        'x-api-key': api_key
    }

    request = {
        'model': model,
        'system': system,
        'query': query,
        'temperature': temperature,
        'lastk': lastk,
        'session_id': session_id,
        'rag_threshold': rag_threshold,
        'rag_usage': rag_usage,
        'rag_k': rag_k
    }

    msg = None

    try:
        response = requests.post(end_point, headers=headers, json=request)

        if response.status_code == 200:
            print("RAG CONTEXT: ",json.loads(response.text)['rag_context'],"\n\n\n\n\n\n")
            msg = json.loads(response.text)['result']
        else:
            msg = f"Error: Received response code {response.status_code}"
    except requests.exceptions.RequestException as e:
        msg = f"An error occurred: {e}"
    return msg	


def calculate_headers_size(headers):
    # HTTP headers typically consist of the key and value, 
    # with a colon and space in between, and each header ends with a CRLF (\r\n).
    return sum(len(key) + len(value) + 4 for key, value in headers.items())

def calculate_multipart_size(multipart_form_data):
    multipart_encoder = MultipartEncoder(fields=multipart_form_data)
    return multipart_encoder.len

def calculate_total_request_size(endpoint, headers, multipart_form_data):
    headers_size = calculate_headers_size(headers)
    multipart_size = calculate_multipart_size(multipart_form_data)

    print("Headers Size (MB): ", headers_size/(1024*1024))
    print("File Size (MB): ", multipart_size/(1024*1024))
    
    # Calculate the total size (in bytes) of the HTTP request
    total_size = len(endpoint) + headers_size + multipart_size
    
    # Convert to megabytes
    total_size_mb = total_size / (1024 * 1024)
    
    print("Request Size (MB): ", total_size_mb)

def upload(multipart_form_data):

    headers = {
        'x-api-key': api_key
    }

    calculate_total_request_size(end_point, headers, multipart_form_data)
    msg = None
    try:
        response = requests.post(end_point, headers=headers, files=multipart_form_data)
        
        if response.status_code == 200:
            msg = "Successfully uploaded. It may take a short while for the document to be added to your context"
        else:
            msg = f"Error: Received response code {response.status_code}"
            print(response)
    except requests.exceptions.RequestException as e:
        msg = f"An error occurred: {e}"
    
    return msg


def pdf_upload(
    path: str,    
    strategy: str | None = None,
    description: str | None = None,
    session_id: str | None = None
    ):
    
    params = {
        'description': description,
        'session_id': session_id,
        'strategy': strategy
    }

    multipart_form_data = {
        'params': (None, json.dumps(params), 'application/json'),
        'file': (None, open(path, 'rb'), "application/pdf")
    }

    # multipart_data = MultipartEncoder(
    #     fields={
    #         'params': (None, json.dumps(params), 'application/json'),
    #         'file': ('filename', open(path, 'rb'), 'application/pdf')
    #     }
    # )

    # # Calculate the size of the multipart encoded data
    # size = multipart_data.len
    # print("size", size/(1024*1024))

    response = upload(multipart_form_data)
    return response

def text_upload(
    text: str,    
    strategy: str | None = None,
    description: str | None = None,
    session_id: str | None = None
    ):
    
    params = {
        'description': description,
        'session_id': session_id,
        'strategy': strategy
    }


    multipart_form_data = {
        'params': (None, json.dumps(params), 'application/json'),
        'text': (None, text, "application/text")
    }


    response = upload(multipart_form_data)
    return response
