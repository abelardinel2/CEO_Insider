import requests

def get_doc4_xml_url(index_json_url):
    response = requests.get(index_json_url)
    response.raise_for_status()
    data = response.json()
    base_url = index_json_url.rsplit("/", 1)[0] + "/"
    for file in data['directory']['item']:
        name = file['name']
        if name.endswith("doc4.xml") and not name.startswith("xsl"):
            return base_url + name
    for file in data['directory']['item']:
        name = file['name']
        if name.endswith("doc4.xml"):
            return base_url + name
    raise Exception("doc4.xml not found")

def download_xml(xml_url):
    response = requests.get(xml_url)
    response.raise_for_status()
    return response.content