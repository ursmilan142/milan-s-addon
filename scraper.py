import requests
from bs4 import BeautifulSoup
import re

def get_streams(content_id):
    if content_id.startswith('fm_'):
        return _scrape_fmovies_streams(content_id)
    return []

def _scrape_fmovies_streams(content_id):
    streams = []
    content_id = content_id.replace('fm_', '').strip('/')
    url = f"https://fmovies24.one/film/{content_id}"
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'lxml')
        
        title_elem = soup.select_one('meta[property="og:title"]')
        desc_elem = soup.select_one('meta[property="og:description"]')
        title = title_elem['content'] if title_elem else 'Unknown'
        description = desc_elem['content'] if desc_elem else ''
        
        script = soup.find('script', id='servers-js-extra')
        if script:
            servers_match = re.search(r'var Servers = ({.*?});', script.string, re.DOTALL)
            if servers_match:
                servers_data = eval(servers_match.group(1))
                stream_keys = ['embedru', 'superembed', 'vidsrc', 'extra1', 'extra2', 'extra3']
                for key in stream_keys:
                    if key in servers_data and servers_data[key]:
                        streams.append({
                            'title': key.capitalize(),
                            'description': description,
                            'url': servers_data[key]
                        })
    except (requests.RequestException, Exception) as e:
        print(f"FMovies stream error: {e}")
    return streams
