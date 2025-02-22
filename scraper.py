import requests
from bs4 import BeautifulSoup
import re

def scrape_fmovies(query):
    """
    Scrape FMovies for search results.
    """
    if not query:
        return []
    url = f"https://fmovies24.one/search/{query}"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    results = []
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'lxml')
        
        for item in soup.select('.film-list .item'):  # Adjust if search page differs
            title_elem = item.select_one('.name')
            link_elem = item.select_one('a')
            poster_elem = item.select_one('img')
            
            if title_elem and link_elem:
                title = title_elem.text.strip()
                link = link_elem['href'].strip('/')  # Clean URL
                poster = poster_elem['data-src'] if poster_elem and 'data-src' in poster_elem.attrs else ''
                results.append({
                    'id': f"fm_{link.split('/')[-1]}",
                    'title': title,
                    'type': 'movie' if '/movie/' in link else 'series',
                    'poster': poster
                })
    except requests.RequestException as e:
        print(f"FMovies scrape error: {e}")
    return results

def get_streams(content_id):
    """
    Get streaming links for a specific movie/series.
    """
    if content_id.startswith('fm_'):
        return _scrape_fmovies_streams(content_id)
    return []

def _scrape_fmovies_streams(content_id):
    """
    Scrape streaming links from FMovies film page.
    """
    streams = []
    content_id = content_id.replace('fm_', '').strip('/')  # Clean ID
    url = f"https://fmovies24.one/film/{content_id}"
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'lxml')
        
        # Extract metadata
        title_elem = soup.select_one('meta[property="og:title"]')
        desc_elem = soup.select_one('meta[property="og:description"]')
        title = title_elem['content'] if title_elem else 'Unknown'
        description = desc_elem['content'] if desc_elem else ''
        
        # Extract streams from Servers object in script
        script = soup.find('script', id='servers-js-extra')
        if script:
            # Extract the Servers object content
            servers_match = re.search(r'var Servers = ({.*?});', script.string, re.DOTALL)
            if servers_match:
                servers_data = eval(servers_match.group(1))  # Safely parse JS object (use json.loads if possible)
                stream_keys = ['embedru', 'superembed', 'vidsrc', 'extra1', 'extra2', 'extra3']
                for key in stream_keys:
                    if key in servers_data and servers_data[key]:
                        streams.append({
                            'title': key.capitalize(),  # e.g., "Embedru" -> "VidPlay"
                            'description': description,
                            'url': servers_data[key]
                        })
    except (requests.RequestException, Exception) as e:
        print(f"FMovies stream error: {e}")
    return streams