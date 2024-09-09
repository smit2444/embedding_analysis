import requests
from bs4 import BeautifulSoup
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
}

url = 'https://dl.acm.org/doi/abs/10.1145/956750.956776'

response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.content, 'html.parser')

abstract_section = soup.find('section', id='abstract')

# Initialize variables to store abstract content
abstract_title = ""
abstract_content = ""
# Check if the abstract section exists and extract content
if abstract_section:
    abstract_title_elem = abstract_section.find('h2', property='name')
    if abstract_title_elem:
        abstract_title = abstract_title_elem.text.strip()

    abstract_content_elem = abstract_section.find('div', role='paragraph')
    if abstract_content_elem:
        abstract_content = abstract_content_elem.text.strip()



print(abstract_content)


