import pandas as pd
import requests
from requests.auth import HTTPBasicAuth

# Configuration
CSV_FILE_PATH = 'path_to_your_csv_file.csv'
WORDPRESS_URL = 'https://789sp.vaetvien.com/wp-json/wp/v2/people'
USERNAME = 'syrx'
PASSWORD = 'P7CZ vviK qFKg JOsC J54q YgL3'

# Read CSV file
data = pd.read_csv('/workspaces/playground_v1/Demo - Sheet1 (1).csv')

# Authentication
auth = HTTPBasicAuth(USERNAME, PASSWORD)

def publish_post(title, acf_fields):
    # Create post data
    post_data = {
        'title': title,
        # 'content': content,
        'status': 'draft',
        'acf': acf_fields  # Include ACF fields directly
    }
    
    # Publish post
    response = requests.post(WORDPRESS_URL, auth=auth, json=post_data)
    
    if response.status_code == 201:  # 201 Created
        print(f'Post "{title}" published successfully.')
    else:
        print(f'Failed to publish post "{title}". Status code: {response.status_code}')
        print(response.json())

# Iterate through rows in the CSV
for _, row in data.iterrows():
    title = row['Title']
    # content = row['content']  # Assuming there's a content column, adjust if necessary

    # Handle relationship fields
    # Convert comma-separated strings of IDs to lists
    who_they_work_with = str(row['Associated People']).split(',') if pd.notna(row['Associated People']) else []
    associated_project = str(row['Project ID']).split(',') if pd.notna(row['Project ID']) else []
    associated_publications = str(row['Publication ID']).split(',') if pd.notna(row['Publication ID']) else []

    # Prepare ACF fields
    acf_fields = {
        'who_they_work_with': who_they_work_with,
        'associated_project': associated_project,
        'associated_publications': associated_publications
    }
    
    publish_post(title, acf_fields)
