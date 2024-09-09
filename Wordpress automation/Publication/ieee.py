import requests
from bs4 import BeautifulSoup

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
}

url = 'https://ieeexplore.ieee.org/abstract/document/6690067/'

response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.content, 'html.parser')

# print(soup)

og_description_meta = soup.find('meta', property='og:description')

# Extract the content attribute if the meta tag exists
if og_description_meta:
    og_description = og_description_meta['content']
    print("Abstract:", og_description)
else:
    print("No meta tag with property='og:description' found.")
