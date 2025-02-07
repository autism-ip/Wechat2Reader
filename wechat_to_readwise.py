import requests
from bs4 import BeautifulSoup
import json
import os
import re
from urllib.parse import urljoin
import base64
import configparser
from pathlib import Path

# Readwise API URL
READWISE_API_URL = "https://readwise.io/api/v2/highlights/"

def get_api_key():
    """从配置文件获取 Readwise API key"""
    config = configparser.ConfigParser()
    config_file = Path(__file__).parent / 'config.ini'
    
    config.read(config_file, encoding='utf-8')
    return config['Readwise']['api_key']

def download_image(img_url):
    """Download image and convert to base64"""
    try:
        response = requests.get(img_url)
        if response.status_code == 200:
            image_data = base64.b64encode(response.content).decode('utf-8')
            return f"data:image/{img_url.split('.')[-1]};base64,{image_data}"
    except Exception as e:
        print(f"Error downloading image {img_url}: {e}")
    return None

def split_content(content, max_length):
    """Split content into chunks of maximum length while preserving HTML structure"""
    soup = BeautifulSoup(content, 'html.parser')
    chunks = []
    current_chunk = ""
    
    def add_chunk(text):
        nonlocal current_chunk, chunks
        # If adding this text would exceed the limit
        if len(current_chunk) + len(text) > max_length:
            # If we already have content in the current chunk
            if current_chunk:
                print(f"Created chunk with length: {len(current_chunk)}")
                chunks.append(f"<div>{current_chunk}</div>")
                current_chunk = ""
            
            # If the text itself is too long, split it
            if len(text) > max_length:
                # For very long text, split it into smaller pieces
                text_soup = BeautifulSoup(text, 'html.parser')
                text_content = text_soup.get_text()
                tag_name = text_soup.find().name if text_soup.find() else 'p'
                
                # Split into sentences
                sentences = re.split(r'([。！？.!?]+)', text_content)
                current_part = ""
                
                for i in range(0, len(sentences), 2):
                    sentence = sentences[i]
                    ending = sentences[i + 1] if i + 1 < len(sentences) else ""
                    full_sentence = sentence + ending
                    
                    # If this sentence alone is too long, split it into characters
                    if len(full_sentence) > max_length:
                        chars = list(full_sentence)
                        temp_part = ""
                        
                        for char in chars:
                            if len(temp_part) + 1 >= max_length - 10:  # Leave room for tags
                                wrapped = f"<{tag_name}>{temp_part}</{tag_name}>"
                                if current_chunk and len(current_chunk) + len(wrapped) > max_length:
                                    chunks.append(f"<div>{current_chunk}</div>")
                                    current_chunk = wrapped
                                else:
                                    current_chunk += wrapped
                                temp_part = char
                            else:
                                temp_part += char
                        
                        if temp_part:
                            wrapped = f"<{tag_name}>{temp_part}</{tag_name}>"
                            if current_chunk and len(current_chunk) + len(wrapped) > max_length:
                                chunks.append(f"<div>{current_chunk}</div>")
                                current_chunk = wrapped
                            else:
                                current_chunk += wrapped
                    else:
                        # Add this sentence to current_part if it fits
                        if len(current_part) + len(full_sentence) <= max_length - 20:  # Leave room for tags
                            current_part += full_sentence
                        else:
                            # Save current_part if it exists
                            if current_part:
                                wrapped = f"<{tag_name}>{current_part}</{tag_name}>"
                                if current_chunk and len(current_chunk) + len(wrapped) > max_length:
                                    chunks.append(f"<div>{current_chunk}</div>")
                                    current_chunk = wrapped
                                else:
                                    current_chunk += wrapped
                            current_part = full_sentence
                
                # Don't forget the last part
                if current_part:
                    wrapped = f"<{tag_name}>{current_part}</{tag_name}>"
                    if current_chunk and len(current_chunk) + len(wrapped) > max_length:
                        chunks.append(f"<div>{current_chunk}</div>")
                        current_chunk = wrapped
                    else:
                        current_chunk += wrapped
            else:
                current_chunk = text
        else:
            current_chunk += text
    
    # Process each element
    for element in soup.find_all(['p', 'div', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'img', 'span']):
        # Special handling for images
        if element.name == 'img':
            img_html = str(element)
            add_chunk(img_html)
            continue
        
        # Handle text elements
        text = element.get_text(strip=True)
        if text:
            element_html = str(element)
            add_chunk(element_html)
    
    # Add the last chunk if there's anything left
    if current_chunk:
        print(f"Created final chunk with length: {len(current_chunk)}")
        chunks.append(f"<div>{current_chunk}</div>")
    
    # Verify all chunks are within size limit
    for i, chunk in enumerate(chunks):
        if len(chunk) > max_length:
            print(f"Warning: Chunk {i+1} is too large ({len(chunk)} chars), splitting further...")
            subchunks = split_content(chunk, max_length)
            chunks[i:i+1] = subchunks
    
    return chunks

def process_wechat_article(url):
    """Process WeChat article content"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Get article title
        title = soup.find('h1', class_='rich_media_title').get_text(strip=True)
        
        # Get article content
        content = soup.find('div', class_='rich_media_content')
        if not content:
            raise Exception("Could not find article content")
        
        # Process images
        for img in content.find_all('img'):
            if img.get('data-src'):
                img_url = img['data-src']
                base64_img = download_image(img_url)
                if base64_img:
                    img['src'] = base64_img
                    del img['data-src']
        
        # Get author
        author = soup.find('a', class_='rich_media_meta rich_media_meta_link rich_media_meta_nickname')
        author = author.get_text(strip=True) if author else "Unknown"
        
        # Split content into chunks
        content_str = str(content)
        print(f"Total content length: {len(content_str)}")
        content_chunks = split_content(content_str, 6000)
        print(f"Split into {len(content_chunks)} chunks")
        
        return {
            'title': title,
            'author': author,
            'content_chunks': content_chunks,
            'url': url
        }
    except Exception as e:
        print(f"Error processing article: {e}")
        return None

def save_to_readwise(article_data):
    """Save processed article to Readwise using REST API"""
    api_key = get_api_key()
    try:
        headers = {
            'Authorization': f'Token {api_key}',
            'Content-Type': 'application/json'
        }
        
        total_chunks = len(article_data['content_chunks'])
        all_responses = []
        
        for i, chunk in enumerate(article_data['content_chunks'], 1):
            chunk_title = f"{article_data['title']} (Part {i}/{total_chunks})"
            print(f"\nSaving chunk {i}/{total_chunks} (length: {len(chunk)})")
            
            payload = {
                'highlights': [{
                    'text': chunk,
                    'title': chunk_title,
                    'author': article_data['author'],
                    'source_url': article_data['url'],
                    'category': 'articles'
                }]
            }
            
            response = requests.post(
                READWISE_API_URL,
                headers=headers,
                json=payload
            )
            
            if response.status_code == 200:
                print(f"Successfully saved part {i}/{total_chunks} to Readwise!")
                all_responses.append(response.json())
            else:
                print(f"Failed to save part {i}/{total_chunks} to Readwise. Status code: {response.status_code}")
                print(f"Response: {response.text}")
                print(f"Chunk length: {len(chunk)}")
                return None
        
        return all_responses
            
    except Exception as e:
        print(f"Error saving to Readwise: {e}")
        return None

def process_article(url):
    """处理单个文章"""
    try:
        article_data = process_wechat_article(url)
        save_to_readwise(article_data)
        return True
    except Exception as e:
        print(f"Error: {str(e)}")
        raise

def main():
    print("Welcome to WeChat Article to Readwise Converter!")
    while True:
        url = input("\nPlease enter the WeChat article URL (or 'q' to quit): ").strip()
        
        if url.lower() == 'q':
            break
            
        if not url:
            print("Please enter a valid URL!")
            continue
            
        print("\nProcessing article...")
        article_data = process_wechat_article(url)
        
        if article_data:
            print("Article processed successfully!")
            print(f"Title: {article_data['title']}")
            print(f"Author: {article_data['author']}")
            print(f"Number of parts: {len(article_data['content_chunks'])}")
            
            print("\nSaving to Readwise...")
            result = save_to_readwise(article_data)
            
            if result:
                print("\nArticle has been successfully saved to Readwise!")
            else:
                print("\nFailed to save article to Readwise. Please try again.")
        else:
            print("\nFailed to process the article. Please check the URL and try again.")

if __name__ == "__main__":
    url = input("请输入微信公众号文章链接：")
    process_article(url)
