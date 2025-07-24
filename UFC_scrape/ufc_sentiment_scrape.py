from playwright.sync_api import sync_playwright
from urllib.parse import urljoin
import re
import traceback
from datetime import datetime
from dateutil.parser import parse as parse_date
import mysql.connector
import time
import requests
from bs4 import BeautifulSoup
import csv
import pandas as pd
import trafilatura

def extract_article_info(url):
    """Extract article information using Trafilatura with BeautifulSoup fallback"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # Try Trafilatura first
        try:
            downloaded = trafilatura.fetch_url(url)
            if downloaded is not None:
                # Extract text content using Trafilatura
                text = trafilatura.extract(downloaded, include_formatting=False, include_links=False, include_images=False)
                
                # Extract metadata using Trafilatura
                metadata = trafilatura.extract_metadata(downloaded)
                title = metadata.title if hasattr(metadata, 'title') else ''
                publish_date = metadata.date if hasattr(metadata, 'date') else ''
                
                # Clean up text
                if text:
                    text = re.sub(r'\s+', ' ', text).strip()
                else:
                    text = "No text found"
                
                return {
                    'title': title or "No title found",
                    'text': text or "No text found",
                    'publish_date': publish_date or "No date found",
                    'url': url
                }
        except Exception as trafilatura_error:
            print(f"Trafilatura failed for {url}: {str(trafilatura_error)}")
        
        # Fallback to BeautifulSoup if Trafilatura fails
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract title
        title = ""
        title_selectors = [
            'h1',
            'title',
            '[property="og:title"]',
            '[name="twitter:title"]'
        ]
        
        for selector in title_selectors:
            title_elem = soup.select_one(selector)
            if title_elem:
                if selector == 'title':
                    title = title_elem.get_text().strip()
                else:
                    title = title_elem.get('content', title_elem.get_text().strip())
                if title:
                    break
        
        # Extract text content
        text = ""
        
        # Remove unwanted elements
        unwanted_selectors = [
            'script', 'style', 'nav', 'header', 'footer', 'aside',
            '.nav', '.header', '.footer', '.sidebar', '.advertisement',
            '.menu', '.navigation', '.social', '.share', '.comments',
            '[class*="nav"]', '[class*="menu"]', '[class*="ad"]',
            '[class*="social"]', '[class*="share"]', '[class*="comment"]'
        ]
        
        for selector in unwanted_selectors:
            for elem in soup.select(selector):
                elem.decompose()
        
        # Priority selectors for article content
        content_selectors = [
            'article',
            'main',
            '.content',
            '.article-content',
            '.post-content',
            '.entry-content',
            '.story-content',
            '.article-body',
            '.post-body',
            '[role="main"]'
        ]
        
        # Try to find main content area
        main_content = None
        for selector in content_selectors:
            main_content = soup.select_one(selector)
            if main_content:
                break
        
        if main_content:
            # Extract paragraphs from main content
            paragraphs = main_content.find_all(['p', 'div'])
            text_parts = []
            
            for p in paragraphs:
                p_text = p.get_text().strip()
                if len(p_text) > 50:  # Reduced minimum length
                    text_parts.append(p_text)
            
            text = ' '.join(text_parts)
        else:
            # Fallback: extract all paragraphs from body
            paragraphs = soup.find_all('p')
            text_parts = []
            
            for p in paragraphs:
                p_text = p.get_text().strip()
                if len(p_text) > 50:  # Reduced minimum length
                    text_parts.append(p_text)
            
            text = ' '.join(text_parts)
        
        # Clean up text
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Extract publish date
        publish_date = ""
        date_selectors = [
            '[property="article:published_time"]',
            '[name="publish_date"]',
            '[name="date"]',
            '.publish-date',
            '.date',
            'time',
            '[class*="date"]',
            '[class*="time"]'
        ]
        
        for selector in date_selectors:
            date_elem = soup.select_one(selector)
            if date_elem:
                date_attr = date_elem.get('content') or date_elem.get('datetime') or date_elem.get_text()
                if date_attr:
                    publish_date = date_attr.strip()
                    break
        
        return {
            'title': title or "No title found",
            'text': text or "No text found",
            'publish_date': publish_date or "No date found",
            'url': url
        }
        
    except Exception as e:
        return {
            'title': f"Error: {str(e)}",
            'text': f"Error: {str(e)}",
            'publish_date': "No date found",
            'url': url
        }

def scrape_ufc_sentiment(topic):
    try:
        articles = []
        
        with sync_playwright() as p:
            # Launch browser with headless=False to show the browser
            browser = p.chromium.launch(headless=True, slow_mo=1000)
            context = browser.new_context()
            page = context.new_page()

            query = topic.replace(' ', '+')
            url = f"https://search.yahoo.com/search?p={query}&fr=news"
            print(f"Navigating to: {url}")
            
            page.goto(url)
            
            # Wait for the page to load
            page.wait_for_load_state('networkidle')
            # Add a small delay to ensure dynamic content loads
            time.sleep(2)
            print("Browser is now open. Press Ctrl+C to close it.")

            # Loop through all possible pages
            current_page = 1
            max_pages = 10  # Capped at 10 pages
            while current_page <= max_pages:
                print(f"Scraping page {current_page}...")
                
                # Wait for the page to load
                page.wait_for_load_state('networkidle')
                time.sleep(3)  # Increased wait time for better page loading

                # Get article links from current page
                anchors = page.query_selector_all("div a.d-ib.va-top.mt-38.mb-4.mxw-100p")
                links = [a.get_attribute("href") for a in anchors]

                print(f"Found {len(links)} articles on page {current_page}")
                
                # If no links found, we might be at the end
                if len(links) == 0:
                    print(f"No articles found on page {current_page}. Stopping.")
                    break
                
                counter = 1
                for link in links:
                    print(f"Link {counter}: {link}")
                    counter += 1
                    articles.append(link)

                # Try to find the next page link with multiple strategies
                next_page_found = False
                try:
                    # Strategy 1: Look for pagination div with next page number
                    pagination_div = page.query_selector("div.pages")
                    if pagination_div:
                        # Look for next page link by number
                        next_page_link = pagination_div.query_selector(f"a[title*='{current_page + 1}']")
                        if next_page_link:
                            print(f"Clicking on page {current_page + 1}...")
                            next_page_link.click()
                            current_page += 1
                            next_page_found = True
                            time.sleep(3)  # Wait for page to load
                    
                    # Strategy 2: Look for "Next" link if first strategy failed
                    if not next_page_found:
                        next_links = page.query_selector_all("a")
                        for link in next_links:
                            link_text = link.inner_text().strip().lower()
                            if link_text in ['next', 'next page', '>', '»']:
                                print(f"Clicking on Next link...")
                                link.click()
                                current_page += 1
                                next_page_found = True
                                time.sleep(3)
                                break
                    
                    # Strategy 3: Look for pagination by URL pattern
                    if not next_page_found:
                        current_url = page.url
                        if 'b=' in current_url:
                            # Extract current page number from URL
                            try:
                                import re
                                match = re.search(r'b=(\d+)', current_url)
                                if match:
                                    current_b = int(match.group(1))
                                    next_b = current_b + 10  # Yahoo typically increments by 10
                                    next_url = current_url.replace(f'b={current_b}', f'b={next_b}')
                                    print(f"Navigating to next page via URL: {next_url}")
                                    page.goto(next_url)
                                    current_page += 1
                                    next_page_found = True
                                    time.sleep(3)
                            except:
                                pass
                    
                    # If no next page found, we're done
                    if not next_page_found:
                        print(f"No more pages found. Stopping at page {current_page}")
                        break
                        
                except Exception as e:
                    print(f"Error navigating to next page: {e}")
                    # Try one more time with a longer wait
                    try:
                        time.sleep(5)
                        page.reload()
                        time.sleep(3)
                    except:
                        print("Failed to reload page. Stopping.")
                        break

            print(f"Total articles scraped: {len(articles)}")
            browser.close()
            
        # Extract article information
        print("\nExtracting article information...")
        article_data = []
        
        # Video platforms to exclude
        video_platforms = [
            'youtube.com', 'youtu.be', 'tiktok.com', 't.co', 'twitter.com',
            'instagram.com', 'facebook.com', 'twitch.tv', 'vimeo.com',
            'dailymotion.com', 'reddit.com', 'pinterest.com', 'snapchat.com',
            'linkedin.com', 'tumblr.com', 'discord.com', 'telegram.org',
            'whatsapp.com', 'signal.org', 'wechat.com', 'line.me',
            'kakao.com', 'naver.com', 'qq.com', 'weibo.com'
        ]
        
        for i, article_url in enumerate(articles, 1):
            try:
                print(f"Processing article {i}/{len(articles)}: {article_url}")
                
                # Skip video platforms
                if any(platform in article_url.lower() for platform in video_platforms):
                    print(f"Skipping video platform: {article_url}")
                    continue
                
                # Extract article information
                article_info = extract_article_info(article_url)
                
                # Skip articles with HTTP errors
                if "Error: 403" in article_info['title'] or "Error: 404" in article_info['title'] or "Error:" in article_info['title']:
                    print(f"Skipping article with HTTP error: {article_url}")
                    continue
                
                # Skip articles with "No text found"
                if article_info['text'] == "No text found":
                    print(f"Skipping article with no text: {article_url}")
                    continue
                
                # Add all articles without filtering
                article_data.append(article_info)
                print(f"Successfully processed: {article_info['title'][:50]}...")
                
            except Exception as e:
                print(f"Error processing article {i}: {e}")
                # Add error entry to keep track of failed URLs
                article_data.append({
                    'title': f"Error processing: {str(e)}",
                    'text': f"Error processing: {str(e)}",
                    'publish_date': "No date found",
                    'url': article_url
                })
                continue
        
        # Save to CSV file
        # Create a clean filename based on the search topic
        search_topic_clean = topic.replace(' ', '_').replace('+', '_').lower()
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        csv_filename = f"../Data/sentiment_datasets/{search_topic_clean}_sentiment_articles_{timestamp}.csv"
        
        # Create the directory if it doesn't exist
        import os
        os.makedirs(os.path.dirname(csv_filename), exist_ok=True)
        
        print(f"\nSaving {len(article_data)} articles to {csv_filename}...")
        
        with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['title', 'text', 'publish_date', 'url']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for article in article_data:
                writer.writerow(article)
        
        print(f"Successfully saved {len(article_data)} articles to {csv_filename}")
        
        # Create a pandas DataFrame for easy analysis
        df = pd.DataFrame(article_data)
        print(f"\nDataFrame created with shape: {df.shape}")
        print("First few rows:")
        print(df.head())
            
    except Exception as e:
        print(f"Error occurred: {e}")
        traceback.print_exc()

# if __name__ == "__main__":
#     scrape_ufc_sentiment("Matthews vs Njokuani")


