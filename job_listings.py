import requests
from bs4 import BeautifulSoup
import pandas as pd

def fetch_job_listings(keyword, page_limit=1):
    base_url = 'https://www.jobindex.dk/jobsoegning.json'
    job_listings = []

    for page in range(1, page_limit+1):
        params = {
            'q' : keyword,
            'page' : page
        }
        response = requests.get(base_url, params=params)
        if response.status_code == 200:
            data = response.json()
            html_content = data.get('result_list_box_html', '')
            soup = BeautifulSoup(html_content, 'html.parser')

            # Find all job ads
            job_ads = soup.find_all('div', class_='jobsearch-result')
            for job_ad in job_ads:
                title = job_ad.find('div', class_ = 'jobad-element-menu-share')['data-share-title']
                url = job_ad.find('div', class_ = 'jobad-element-menu-share')['data-share-url']
                published_tag = job_ad.find('time')
                published_date = published_tag['datetime'] if published_tag else 'Unknown'
                job_listings.append((title, published_date, url))
        else:
            break

    return job_listings

# Example usage
keyword = 'data'
job_listings = fetch_job_listings(keyword, page_limit=10)
df = pd.DataFrame(job_listings, columns=['Title', 'Published Date', 'URL'])

# saving to csv
df.to_csv('job_listings.csv', index=False)

df.head()