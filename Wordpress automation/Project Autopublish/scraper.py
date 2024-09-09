import requests
import json
import re

# Step 1: Scrape the content from the API endpoint
url = "https://www.research.gov/awardapi-service/v1/awards.json?keyword=Jaideep+Vaidya&rpp=120&printFields=title,publicationResearch,estimatedTotalAmt,abstractText,fundProgramName,agency"
response = requests.get(url)

if response.status_code == 200:
    data = response.json()
else:
    print(f"Failed to fetch data: {response.status_code}")
    data = None

if data:
    awards = data.get('response', {}).get('award', [])

    results = []
    for award in awards:
        title = award.get('title', '')
        abstract_text = award.get('abstractText', '')
        agency = award.get('agency', '')
        program_name = award.get('fundProgramName', '')
        funds_obligated_amt = award.get('estimatedTotalAmt', '')

        publication_research = award.get('publicationResearch', [])
        
        authors = set()
        for pub in publication_research:
            parts = pub.split('~')
            if len(parts) > 3:
                author_string = parts[3]
                individual_authors = re.split(r',\s*|\sand\s', author_string)
                authors.update(individual_authors)
        
        unique_authors = ', '.join(authors)

        result = {
            "title": title,
            "abstractText": abstract_text,
            "fundsObligatedAmt": funds_obligated_amt,
            "agency": agency,
            "fundProgramName": program_name,
            "authors": unique_authors
        }
        results.append(result)

#     final_output = json.dumps(results, indent=4)
#     print(final_output)
# else:
#     print("No data available")


    output_filename = "results.json"
    with open(output_filename, 'w') as outfile:
        json.dump(results, outfile, indent=4)

    print(f"Results have been saved to {output_filename}")

