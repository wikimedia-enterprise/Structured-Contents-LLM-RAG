import pandas as pd
from dotenv import load_dotenv

from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import requests

from tqdm import tqdm

import os
import threading
from concurrent.futures import ThreadPoolExecutor

# Load environment variables
load_dotenv()

# Setup a HTTP session with retries
session = requests.Session()
retries = Retry(total=5, backoff_factor=0.1)  # Retry up to 5 times with a backoff factor
session.mount('http://', HTTPAdapter(max_retries=retries))


# Function to login and get the bearer token
def get_bearer_token():
    url = "https://auth.enterprise.wikimedia.com/v1/login"
    username = os.getenv('WIKI_API_USERNAME')
    password = os.getenv('WIKI_API_PASSWORD')

    # Try to fetch the access token
    try:
        response = session.post(url, json={"username": username, "password": password}, timeout=5)
        data = response.json()
        return data['access_token']

    except requests.exceptions.ConnectionError:
        print("Connection error occurred")
    except requests.exceptions.Timeout:
        print("Request timed out")
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")

    return ""

# Function to fetch article data from Wikipedia
def fetch_article(title, token):
    url = f"https://api.enterprise.wikimedia.com/v2/structured-contents/{title.replace(' ', '_')}"
    headers = {'Authorization': f'Bearer {token}'}

    # Try to fetch the article data
    try:
        response = session.post(url, json={"fields": ["identifier", "url","name", "article_sections"], "filters": [{"field":"is_part_of.identifier", "value":"enwiki"}]}, headers=headers, timeout=10)
        article_data = response.json()

        return article_data

    except requests.exceptions.ConnectionError:
        print("Connection error occurred")
    except requests.exceptions.Timeout:
        print("Request timed out")
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")

    return ""

def clean_text(article_data):
    result = []

    # Iterate through each section in the article data
    for section in article_data:
        # Retrieve and concatenate the name and value of each section and its paragraphs
        if 'has_parts' in section:
            if 'name' in section:
                result.append(f"{section['name']}.")

            for part in section['has_parts']:
                if 'value' in part:
                    result.append(f"{part['value']}")

    # Join all elements in the result list with a space as separator
    return ' '.join(result)


# Reading CSV to get article titles
def read_titles_from_csv(file_path):
    df = pd.read_csv(file_path)
    return df.iloc[:, 2].tolist()  # Assuming the third column contains titles


# Function to save articles information to a CSV file
def save_to_csv(articles_info, output_file_path):
    # Create a DataFrame from the list of tuples
    df = pd.DataFrame(articles_info, columns=['Identifier', 'URL', 'Title', 'Cleaned Text'])
    # Save the DataFrame to a CSV file
    df.to_csv(output_file_path, index=False, header=False)

# Integration into the main function
def pipelineV1(file_path, output_file_path):
     titles = read_titles_from_csv(file_path)
     token = get_bearer_token()
     articles = []

     for title in tqdm(titles, total=len(titles), desc="Downloading and cleaning Wikipedia articles"):
         items = fetch_article(title, token)
         if not items or not isinstance(items, list):
            continue

         article = items[0] # We only want the first article
         if 'article_sections' in article :
            cleaned_text = clean_text(article['article_sections'])
            articles.append((article['identifier'], article['url'], article['name'], cleaned_text))

     # Save to CSV
     save_to_csv(articles, output_file_path)


def pipelineV2(file_path, output_file_path):
    titles = read_titles_from_csv(file_path)
    token = get_bearer_token()
    articles = []
    lock = threading.Lock()  # Create a lock for thread-safe appends to the articles list

    # Define a function that each thread will execute
    def process_article(title):
        items = fetch_article(title, token)
        if not items or not isinstance(items, list):
            return

        article = items[0]  # We only want the first article
        if 'article_sections' in article :
            cleaned_text = clean_text(article['article_sections'])
            # Lock the shared resource, append the result, then unlock
            with lock:
                articles.append((article['identifier'], article['url'], article['name'], cleaned_text))

    # Create a ThreadPoolExecutor to manage a pool of threads
    cores = os.cpu_count() * 3  # Use twice the number of CPU cores
    with ThreadPoolExecutor(max_workers=cores) as executor:
        # Use tqdm for progress bar in threading context
        list(tqdm(executor.map(process_article, titles), total=len(titles), desc="Downloading and cleaning Wikipedia articles"))

    # Save to CSV
    save_to_csv(articles, output_file_path)


if __name__ == '__main__':
    # Get the absolute path of the directory containing the script
    dir_path = os.path.dirname(os.path.abspath(__file__))

    # Properly join paths with the directory path
    inputFile = os.path.join(dir_path, 'dataset', 'titles_en.csv')
    outputV1 = os.path.join(dir_path, 'dataset', 'en2.csv')
    outputV2 = os.path.join(dir_path, 'dataset', 'en3.csv')

    # Run the pipeline sequentially
    #pipelineV1(inputFile, outputV1)  # 1 thread took 9 minutes

    # Run the pipeline with threading
    pipelineV2(inputFile, outputV2)   # 24 threads took 35 seconds
