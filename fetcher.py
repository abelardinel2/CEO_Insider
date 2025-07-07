
import requests

def get_doc4_xml_url(index_json_url):
    response = requests.get(index_json_url)
    response.raise_for_status()
    data = response.json()
    for file in data['directory']['item']:
        if file['name'].endswith('.xml'):
            return index_json_url.replace('index.json', '') + file['name']
    raise Exception("doc4.xml not found")

def download_xml(xml_url):
    response = requests.get(xml_url)
    response.raise_for_status()
    return response.content
