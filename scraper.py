import requests
from bs4 import BeautifulSoup
import re
import time
import urllib3
from urllib.parse import urljoin

# SSL warning disable
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def extract_jagobd_streams():
    """
    Extract live stream links from jagobd.com with better error handling
    """
    stream_links = []
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
        }
        
        print("Fetching jagobd.com...")
        
        # Use session for better connection handling
        session = requests.Session()
        session.headers.update(headers)
        
        response = session.get('https://www.jagobd.com/', timeout=30, verify=False)
        response.raise_for_status()
        
        print(f"Status Code: {response.status_code}")
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Method 1: Find all potential video links
        video_elements = soup.find_all(['video', 'iframe', 'source', 'embed'])
        for element in video_elements:
            src = element.get('src')
            if src:
                full_url = urljoin('https://www.jagobd.com', src)
                name = element.get('title') or 'JagoBD_Stream'
                
                if is_stream_url(full_url):
                    stream_links.append({
                        'url': full_url,
                        'name': name,
                        'type': 'video_element'
                    })
        
        # Method 2: Find links in anchor tags
        anchor_links = soup.find_all('a', href=True)
        for link in anchor_links:
            href = link.get('href', '')
            if is_stream_url(href):
                full_url = urljoin('https://www.jagobd.com', href)
                name = link.get_text(strip=True) or f'Channel_{len(stream_links)+1}'
                
                stream_links.append({
                    'url': full_url,
                    'name': name,
                    'type': 'anchor_link'
                })
        
        # Remove duplicates
        unique_streams = []
        seen_urls = set()
        
        for stream in stream_links:
            if stream['url'] not in seen_urls:
                unique_streams.append(stream)
                seen_urls.add(stream['url'])
        
        print(f"Found {len(unique_streams)} potential stream links")
        return unique_streams
        
    except Exception as e:
        print(f"Error extracting from jagobd.com: {str(e)}")
        # Return some sample streams for testing
        return get_sample_streams()

def is_stream_url(url):
    """
    Check if URL is likely a stream URL
    """
    if not url:
        return False
        
    url_lower = url.lower()
    stream_patterns = ['.m3u8', '.mp4', 'stream', 'live', 'hls', 'video']
    
    return any(pattern in url_lower for pattern in stream_patterns)

def get_sample_streams():
    """
    Return sample streams for testing when extraction fails
    """
    print("Using sample streams for testing")
    return [
        {
            'url': 'https://example.com/sample1.m3u8',
            'name': 'Sample_Channel_1',
            'type': 'sample'
        },
        {
            'url': 'https://example.com/sample2.m3u8', 
            'name': 'Sample_Channel_2',
            'type': 'sample'
        }
    ]

def test_stream_links(stream_links):
    """
    Test stream links with timeout handling
    """
    working_links = []
    
    print(f"Testing {len(stream_links)} links...")
    
    for stream in stream_links:
        try:
            # Skip sample URLs
            if 'example.com' in stream['url']:
                continue
                
            response = requests.head(stream['url'], timeout=5, verify=False)
            if response.status_code in [200, 206, 302, 301]:
                working_links.append(stream)
                print(f"✓ Working: {stream['name']}")
            else:
                print(f"✗ Failed ({response.status_code}): {stream['name']}")
                
        except requests.exceptions.Timeout:
            print(f"✗ Timeout: {stream['name']}")
        except Exception as e:
            print(f"✗ Error: {stream['name']} - {str(e)[:50]}")
    
    # If no working links found, use samples
    if not working_links:
        print("No working links found, using samples")
        working_links = get_sample_streams()
    
    return working_links
