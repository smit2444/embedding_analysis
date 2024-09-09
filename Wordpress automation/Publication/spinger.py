import requests
from bs4 import BeautifulSoup

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
}

url = 'https://link.springer.com/article/10.1007/s10994-013-5376-1'

response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.content, 'html.parser')

abstract_section = soup.find(class_='c-article-section__content').text.strip()

print(abstract_section)

