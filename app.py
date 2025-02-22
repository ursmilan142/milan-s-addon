from flask import Flask, jsonify, request, Response
import requests
from bs4 import BeautifulSoup
from scraper import get_streams

app = Flask(__name__)

def respond_with(data):
    """Helper to add CORS headers to responses."""
    resp = jsonify(data)
    resp.headers['Access-Control-Allow-Origin'] = '*'
    resp.headers['Access-Control-Allow-Headers'] = '*'
    return resp

@app.route('/manifest.json')
def manifest():
    return respond_with({
        "id": "com.example.fmovies-addon",
        "version": "1.0.0",
        "name": "FMovies Addon",
        "description": "Stream movies and series from FMovies24.one",
        "resources": ["stream", "meta"],
        "types": ["movie", "series"],
        "idPrefixes": ["fm_"]
    })

@app.route('/stream/<type>/<id>.json')
def stream(type, id):
    if type not in ["movie", "series"] or not id.startswith('fm_'):
        return respond_with({"streams": []}), 400
    
    streams = get_streams(id)
    if not streams:
        return respond_with({"streams": []}), 404
    
    formatted_streams = [
        {
            "name": stream['title'],
            "description": stream.get('description', ''),
            "url": stream['url'].replace('\\/', '/'),
            "behaviorHints": {"notWebReady": True}
        }
        for stream in streams
    ]
    return respond_with({"streams": formatted_streams})

@app.route('/meta/<type>/<id>.json')
def meta(type, id):
    if type not in ["movie", "series"] or not id.startswith('fm_'):
        return respond_with({"meta": {}}), 400
    
    content_id = id.replace('fm_', '').strip('/')
    url = f"https://fmovies24.one/{content_id}"  # Adjusted URL based on your HTML
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    try:
        print(f"Fetching meta for URL: {url}")
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'lxml')
        print(f"Page content length: {len(response.text)}")
        
        title_elem = soup.select_one('meta[property="og:title"]') or soup.select_one('h1.entry-title')
        title = title_elem['content'] if title_elem and 'content' in title_elem.attrs else (title_elem.text if title_elem else 'Unknown')
        
        desc_elem = soup.select_one('meta[property="og:description"]') or soup.select_one('.description p')
        description = desc_elem['content'] if desc_elem and 'content' in desc_elem.attrs else (desc_elem.text if desc_elem else '')
        
        poster_elem = soup.select_one('.poster img')
        poster = poster_elem['src'] if poster_elem and 'src' in poster_elem.attrs else ''
        
        year_elem = soup.select_one('.meta .year')
        year = year_elem.text.strip() if year_elem else ''
        
        genres = [a.text.strip() for a in soup.select('.detail div:contains("Genre") a')] or []
        director_elem = soup.select_one('.detail div:contains("Director") a')
        director = director_elem.text.strip() if director_elem else ''
        cast = [a.text.strip() for a in soup.select('.casts a')] or []
        
        meta_data = {
            "id": id,
            "type": type,
            "name": title,
            "description": description,
            "poster": poster,
            "year": year,
            "genres": genres,
            "director": director,
            "cast": cast
        }
        print(f"Meta data: {meta_data}")
        return respond_with({"meta": meta_data})
    except Exception as e:
        print(f"Meta scrape error: {e}")
        return respond_with({"meta": {}}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
