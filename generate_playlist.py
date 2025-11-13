import json
from datetime import datetime
from scraper import extract_jagobd_streams, test_stream_links

def create_m3u_playlist(streams, output_file='playlist.m3u'):
    """
    Create M3U playlist file from stream links
    """
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            # M3U header
            f.write('#EXTM3U\n')
            f.write(f'# Playlist Generated from jagobd.com\n')
            f.write(f'# Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n')
            f.write(f'# Total Channels: {len(streams)}\n\n')
            
            # Add each channel to playlist
            for i, stream in enumerate(streams, 1):
                channel_name = clean_channel_name(stream['name'])
                stream_url = stream['url']
                
                # EXTINF line with channel info
                f.write(f'#EXTINF:-1 tvg-id="channel{i}" tvg-name="{channel_name}" group-title="JagoBD",{channel_name}\n')
                
                # Stream URL
                f.write(f'{stream_url}\n\n')
            
        print(f"Playlist created: {output_file}")
        return True
        
    except Exception as e:
        print(f"Error creating playlist: {e}")
        return False

def clean_channel_name(name):
    """
    Clean channel name for M3U format
    """
    # Remove special characters that might break M3U format
    cleaned = re.sub(r'[<>:"/\\|?*]', '', name)
    cleaned = cleaned.replace('"', "'")
    return cleaned.strip()

def main():
    print("Starting JagoBD stream extraction...")
    
    # Extract links from website
    all_links = extract_jagobd_streams()
    
    if not all_links:
        print("No links found. Creating empty playlist.")
        with open('playlist.m3u', 'w') as f:
            f.write('#EXTM3U\n')
            f.write('# No streams found from jagobd.com\n')
        return
    
    # Test which links are working
    working_links = test_stream_links(all_links)
    
    # Create playlist
    if working_links:
        success = create_m3u_playlist(working_links)
        if success:
            print(f"Successfully created playlist with {len(working_links)} channels")
        else:
            print("Failed to create playlist")
    else:
        print("No working links found")
        # Create empty playlist
        with open('playlist.m3u', 'w') as f:
            f.write('#EXTM3U\n')
            f.write('# No working streams found\n')

if __name__ == "__main__":
    main()
