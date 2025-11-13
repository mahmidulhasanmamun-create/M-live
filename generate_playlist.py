import os
from datetime import datetime
from scraper import extract_jagobd_streams, test_stream_links

def create_m3u_playlist(streams, output_file='playlist.m3u'):
    """
    Create M3U playlist file from stream links
    """
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('#EXTM3U\n')
            f.write(f'# JagoBD Playlist - Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n')
            f.write(f'# Total Channels: {len(streams)}\n\n')
            
            for i, stream in enumerate(streams, 1):
                channel_name = stream['name']
                stream_url = stream['url']
                
                f.write(f'#EXTINF:-1 tvg-id="ch{i}" tvg-name="{channel_name}",{channel_name}\n')
                f.write(f'{stream_url}\n\n')
            
        print(f"Successfully created {output_file}")
        return True
        
    except Exception as e:
        print(f"Error creating playlist: {e}")
        return False

def main():
    print("=== JagoBD IPTV Playlist Generator ===")
    
    # Extract streams
    streams = extract_jagobd_streams()
    
    # Test streams
    working_streams = test_stream_links(streams)
    
    # Create playlist
    if create_m3u_playlist(working_streams):
        print(f"Playlist generated with {len(working_streams)} channels")
    else:
        print("Failed to generate playlist")
        
    print("=== Process Complete ===")

if __name__ == "__main__":
    main()
