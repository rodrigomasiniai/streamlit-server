import os
import re
import requests
import uuid
import zipfile
import hashlib
import shutil
import streamlit as st
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

# Function to validate URLs
def is_valid(url):
    parsed = urlparse(url)
    return bool(parsed.netloc) and bool(parsed.scheme)

# Function to find files on webpage
def find_files(url, soup, file_type):
    files = []
    if file_type == "image":
        tags = ['jpg', 'jpeg', 'png', 'svg', 'gif']
        for tag in soup.find_all('img'):
            file = tag.get('src')
            if any(tag in file for tag in tags):
                file_url = file
                if not is_valid(file_url):
                    file_url = urljoin(url, file_url)
                files.append(file_url)
    elif file_type == "text":
        text_tags = ['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'span', 'strong']
        for tag in text_tags:
            for element in soup.find_all(tag):
                files.append(element.get_text())
    else:
        for link in soup.find_all('a'):
            file = link.get('href')
            if file_type in file:
                file_url = file
                if not is_valid(file_url):
                    file_url = urljoin(url, file_url)
                files.append(file_url)
    return files


# Function to download files
def download_files(urls, folder_name):
    os.makedirs(folder_name, exist_ok=True)
    for i, url in enumerate(urls):
        response = requests.get(url, stream=True)
        file_extension = url.split(".")[-1].split("&")[0]
        url_hash = hashlib.md5(url.encode()).hexdigest()
        unique_id = str(uuid.uuid4())[:8]
        file_name = f'{url_hash}-{unique_id}.{file_extension}'
        file_name = file_name[:255]  # Truncate the file name to avoid exceeding the limit
        file_name = re.sub(r'[\\/:"*?<>|]+', '_', file_name)  # Replace special characters with underscores
        with open(f'{folder_name}/{file_name}', 'wb') as out_file:
            out_file.write(response.content)
        print(f"Downloaded file: {file_name}")

# Function to create zip file
def create_zip_file(folder_name):
    # Only create zip file if there are files in the directory
    if os.listdir(folder_name):
        with zipfile.ZipFile(f'{folder_name}.zip', 'w') as zipf:
            for file in os.listdir(folder_name):
                zipf.write(f'{folder_name}/{file}')
        with open(f'{folder_name}.zip', 'rb') as f:
            bytes_content = f.read()
        return bytes_content
    else:
        return None


# Function to scrape website
def scrape_website(url, images=False, text=False):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Raise an exception if the GET request was unsuccessful
    except (requests.exceptions.RequestException, ValueError):
        raise st.error(f"Unable to access URL: {url}")
        return None, None

    soup = BeautifulSoup(response.content, 'html.parser')

    # Clear the contents of the folders
    if images:
        shutil.rmtree('images', ignore_errors=True)
    if text:
        shutil.rmtree('text', ignore_errors=True)

    # Download files
    if images:
        image_urls = find_files(url, soup, 'image')
        download_files(image_urls, 'images')
    if text:
        text_content = find_files(url, soup, 'text')
        os.makedirs('text', exist_ok=True)  # Make sure the directory exists before writing
        if text_content:  # Only create the file if there is text to write
            with open('text/content.txt', 'w') as text_file:
                for line in text_content:
                    text_file.write(line + '\n')

    # Create zip files and return paths
    images_zip_file, text_zip_file = None, None
    if images and os.path.exists('images') and os.listdir('images'):
        images_zip_file = create_zip_file('images')
    if text and os.path.exists('text') and os.listdir('text'):
        text_zip_file = create_zip_file('text')

    return images_zip_file, text_zip_file

def web_scraping(url, file_types):
    # Check if the URL is empty
    if not url:
        st.error("URL cannot be empty.")
        return None, None

    # Check if the URL begins with https://
    if not url.startswith("https://"):
        st.error("The URL must begin with https://")
        return None, None

    # Check if at least one checkbox is selected
    if not file_types:
        st.error("At least one media type must be selected.")
        return None, None

    images = "Images" in file_types
    text = "Text" in file_types
    return scrape_website(url, images, text)

st.title('Web Scraping App')

url = st.text_input("Website", value='', help="Example: https://en.wikipedia.org/wiki/Main_Page")
file_types = st.multiselect("Media types", ["Images", "Text"], default=["Images"])
scrape_button = st.button('Scrape')

if scrape_button:
    images_zip_file, text_zip_file = web_scraping(url, file_types)
    if images_zip_file:
        st.download_button(label="Download Images ZIP-file", data=images_zip_file, file_name='images.zip')
    if text_zip_file:
        st.download_button(label="Download Text ZIP-file", data=text_zip_file, file_name='text.zip')