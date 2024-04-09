from fastapi import FastAPI
from typing import List
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import pandas as pd

app = FastAPI()

# Function to fetch job listings
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
                published_tag = job_ad.find('time')
                published_date = published_tag['datetime'] if published_tag else 'unknown'
                
                # Extracting location
                location_tag = job_ad.find('div', class_='jobad-element-area')
                location = location_tag.find('span', class_='jix_robotjob--area').text.strip() if location_tag and location_tag.find('span', class_='jix_robotjob--area') else 'unknown'

                # Compare published date with yesterday's date
                if published_date.startswith(yesterday_date):
                    job_listings.append({'title': title, 'published_date': published_date, 'location': location, 'url': url})
                else:
                    # Since the posts are ordered by date, if we hit a post that is not from yesterday, we can stop.
                    break
        else:
            break
    
    return job_listings

# Function to save job listings to CSV file
def save_job_listings_to_csv(job_listings, filename='job_listings.csv'):
    df = pd.DataFrame(job_listings)
    df.to_csv(filename, mode='a', header=False, index=False)  # Append to CSV file without writing header

# Endpoint to fetch and save job listings
@app.get("/update-job-listings/{geoareaid}")
def update_job_listings(geoareaid: str):
    job_listings = fetch_job_listings(geoareaid, page_limit=10)
    save_job_listings_to_csv(job_listings)
    return {"message": "Job listings updated successfully."}