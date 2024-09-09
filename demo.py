import requests
from bs4 import BeautifulSoup

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
}

url = 'https://scholar.google.com/citations?view_op=view_citation&hl=en&user=SENrqMcAAAAJ&citation_for_view=SENrqMcAAAAJ:9yKSN-GCB0IC'

response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.content, 'html.parser')

journal_link = soup.find('a', class_='gsc_oci_title_link').get('href')


print(journal_link)

