import requests
from bs4 import BeautifulSoup
import time

headers = {
   "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
}

# Function to scrape details from IEEE
def scrape_ieee(url):
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    og_description_meta = soup.find('meta', property='og:description')
    if og_description_meta:
        return og_description_meta['content'].strip()
    return None

# Function to scrape details from Springer
def scrape_springer(url):
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    abstract_section = soup.find(class_='c-article-section__content')
    if abstract_section:
        return abstract_section.text.strip()
    return None

# Function to scrape details from ACM DL
def scrape_acm_dl(url):
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    abstract_section = soup.find('section', id='abstract')
    if abstract_section:
        abstract_content_elem = abstract_section.find('div', role='paragraph')
        if abstract_content_elem:
            return abstract_content_elem.text.strip()
    return None

# Function to fetch publication links and details from Google Scholar profile
def fetch_and_publish_to_wordpress(profile_url, wp_url, username, app_password, post_type, custom_fields):
    response = requests.get(profile_url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    for item in soup.select('.gsc_a_tr'):
        gs_pub_link = 'https://scholar.google.com' + item.select('a')[0]['href']
        stage2_response = requests.get(gs_pub_link, headers=headers)
        stage2_soup = BeautifulSoup(stage2_response.content, 'html.parser')
        journal_link = stage2_soup.find('a', class_='gsc_oci_title_link').get('href')
        
        authors = stage2_soup.find(class_='gsc_oci_value').text.strip()
        publication_date = stage2_soup.find_all(class_='gsc_oci_value')[1].text.strip()
        book = stage2_soup.find_all(class_='gsc_oci_value')[2].text.strip()
        
        domain = None
        if 'ieee.org' in journal_link:
            domain = 'ieee'
        elif 'springer.com' in journal_link:
            domain = 'springer'
        elif 'dl.acm.org' in journal_link:
            domain = 'acm_dl'

        abstract = None
        if domain:
            if domain == 'ieee':
                abstract = scrape_ieee(journal_link)
            elif domain == 'springer':
                abstract = scrape_springer(journal_link)
            elif domain == 'acm_dl':
                abstract = scrape_acm_dl(journal_link)

        data = {
            "title": item.select('.gsc_a_at')[0].text.strip(),
            "content": f"Authors: {authors}<br>Publication Date: {publication_date}<br>Abstract: {abstract}<br>Journal: {journal_link}<br><a href='{gs_pub_link}'>Link to Publication</a>",
            "status": "publish",
            "type": post_type,
            "fields": {
                custom_fields[0]: authors,
                # custom_fields[1]: publication_date,
                custom_fields[1]: abstract if abstract else '',
                custom_fields[2]: journal_link,
                custom_fields[3]: 'PDF',
                custom_fields[4]: journal_link
            }
        }

        response = requests.post(
            f"{wp_url}/wp-json/wp/v2/publication",
            auth=requests.auth.HTTPBasicAuth(username, app_password),
            json=data
        )
        if response.status_code == 201:
            print(f"Published: {data['title']}")
        else:
            print(f"Failed to publish: {data['title']}, Status Code: {response.status_code}")

        time.sleep(5)  # Delay before making the next request

if __name__ == "__main__":
    # Google Scholar profile URL
    profile_url = "https://scholar.google.com/citations?hl=en&user=SENrqMcAAAAJ"
    
    # WordPress credentials and URL
    wp_url = "https://789sp.vaetvien.com"
    username = "syrx"
    app_password = "P7CZ vviK qFKg JOsC J54q YgL3"

    # Custom post type and custom fields
    post_type = "publication"  # Replace with your custom post type
    custom_fields = ["publication_authors", "abstract_publications", "publication_link", "link_title_1", "link_space_1"]

    # Fetch publications and publish to WordPress
    fetch_and_publish_to_wordpress(profile_url, wp_url, username, app_password, post_type, custom_fields)
