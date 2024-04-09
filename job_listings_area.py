import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import pandas as pd

def fetch_job_listings(geoareaid, page_limit=1):
    base_url = 'https://www.jobindex.dk/jobsoegning.json'
    job_listings = []

    # Calculate yesterday's date
    yesterday_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')

    for page in range(1, page_limit+1):
        params = {
            'geoareaid': geoareaid,
            'page': page
        }
        response = requests.get(base_url, params=params)
        if response.status_code == 200:
            data = response.json()
            html_content = data.get('result_list_box_html', '')
            soup = BeautifulSoup(html_content, 'html.parser')

            # Find all job ads
            job_ads = soup.find_all('div', class_='jobsearch-result')
            for job_ad in job_ads:
                title = job_ad.find('div', class_='jobad-element-menu-share')['data-share-title']
                url = job_ad.find('div', class_='jobad-element-menu-share')['data-share-url']
                # Extracting location
                location_tag = job_ad.find('div', class_='jobad-element-area')
                location = location_tag.find('span', class_='jix_robotjob--area').text.strip() if location_tag and location_tag.find('span', class_='jix_robotjob--area') else 'unknown'
                published_tag = job_ad.find('time')
                published_date = published_tag['datetime'] if published_tag else 'unknown'
                

                # Compare published date with yesterday's date
                if published_date.startswith(yesterday_date):
                    job_listings.append([title, published_date, location, url])
                else:
                    # Since the posts are ordered by date, if we hit a post that is not from yesterday, we can stop.
                    break
        else:
            break
    
    return job_listings

# Gettings yesterdays job listings
geoareaid = ''
job_listings = fetch_job_listings(geoareaid, page_limit=100)
df = pd.DataFrame(job_listings, columns=['Title', 'Published Date', 'Location', 'URL'])

# saving to csv
df.to_csv('job_listings_area.csv', index=False)

df.head()
