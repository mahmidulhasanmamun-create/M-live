import requests
from bs4 import BeautifulSoup
import re
import time

def extract_jagobd_streams():
    """
    Extract live stream links from jagobd.com
    """
    stream_links = []
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        print("Fetching jagobd.com...")
        response = requests.get('https://www.jagobd.com/', headers=headers, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Method 1: Look for video players and iframes
        video_players = soup.find_all(['video', 'iframe', 'embed', 'object'])
        for player in video_players:
            src = player.get('src')
            if src:
                full_url = make_absolute_url(src)
                if is_stream_url(full_url):
                    name = player.get('title') or player.get('alt') or 'JagoBD_Stream'
                    stream_links.append({
                        'url': full_url,
                        'name': name,
                        'type': 'direct'
                    })
        
        # Method 2: Look for links containing stream keywords
        stream_keywords = ['m3u8', 'stream', 'live', 'hls', 'rtmp', 'rtsp', 'flv']
        all_links = soup.find_all('a', href=True)
        
        for link in all_links:
            href = link.get('href', '')
            text = link.get_text().strip()
            
            if any(keyword in href.lower() for keyword in stream_keywords):
                full_url = make_absolute_url(href)
                name = text or f'Channel_{len(stream_links)+1}'
                stream_links.append({
                    'url': full_url,
                    'name': name,
                    'type': 'link'
                })
        
        # Method 3: Look for script tags containing stream URLs
        scripts = soup.find_all('script')
        for script in scripts:
            if script.string:
                script_content = script.string
                # Look for URLs in scripts
                url_patterns = [
                    r'https?://[^\s"\']+\.m3u8[^\s"\']*',
                    r'https?://[^\s"\']+\.mp4[^\s"\']*',
                    r'https?://[^\s"\']+\.ts[^\s"\']*',
                    r'file[=:]["\']([^"\']+)["\']',
                    r'src[=:]["\']([^"\']+)["\']'
                ]
                
                for pattern in url_patterns:
                    matches = re.finditer(pattern, script_content, re.IGNORECASE)
                    for match in matches:
                        url = match.group(0) if match.group(0) else match.group(1)
                        if url and is_stream_url(url):
                            full_url = make_absolute_url(url)
                            stream_links.append({
                                'url': full_url,
                                'name': f'Script_Stream_{len(stream_links)+1}',
                                'type': 'script'
                            })
        
        # Remove duplicates
        unique_links = []
        seen_urls = set()
        for stream in stream_links:
            if stream['url'] not in seen_urls:
                unique_links.append(stream)
                seen_urls.add(stream['url'])
        
        print(f"Found {len(unique_links)} unique stream links")
        return unique_links
        
    except Exception as e:
        print(f"Error extracting streams: {e}")
        return []

def make_absolute_url(url):
    """
    Convert relative URL to absolute URL
    """
    if url.startswith('//'):
        return 'https:' + url
    elif url.startswith('/'):
        return 'https://www.jagobd.com' + url
    elif not url.startswith('http'):
        return 'https://www.jagobd.com/' + url
    else:
        return url

def is_stream_url(url):
    """
    Check if URL is likely a stream URL
    """
    stream_patterns = [
        r'\.m3u8', r'\.mp4', r'\.ts', r'\.flv', 
        r'\.avi', r'\.mkv', r'rtmp://', r'rtsp://',
        r'stream', r'live', r'hls', r'video'
    ]
    
    url_lower = url.lower()
    return any(pattern in url_lower for pattern in stream_patterns)

def test_stream_links(stream_links, max_test=10):
    """
    Test if stream links are working (limited testing to avoid timeouts)
    """
    working_links = []
    
    print(f"Testing {min(len(stream_links), max_test)} links...")
    
    for i, stream in enumerate(stream_links[:max_test]):
        try:
            # Quick head request to check if URL is accessible
            response = requests.head(stream['url'], timeout=5, allow_redirects=True)
            if response.status_code in [200, 206, 302]:
                working_links.append(stream)
                print(f"✓ Working: {stream['name']}")
            else:
                print(f"✗ Not working ({response.status_code}): {stream['name']}")
        except requests.exceptions.Timeout:
            print(f"✗ Timeout: {stream['name']}")
        except Exception as e:
            print(f"✗ Error: {stream['name']} - {str(e)[:50]}")
    
    return working_links
