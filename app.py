from flask import Flask, jsonify, request, Response, send_file
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
        "id": "com.milan-s-addon",
        "version": "1.0.0",
        "name": "🤫Milan's Free Movies and Series🤫",
        "description": "Stream movies and series for 💯FREE💯",
        "resources": ["stream", "meta"],
        "types": ["movie", "series"],
        "idPrefixes": ["fm_", "tt"],  # Add "tt" to support IMDb IDs
        "logo": f"https://{request.host}/logo.jpg"
    })

@app.route('/stream/<type>/<id>.json')
def stream(type, id):
    print(f"Request received: type={type}, id={id}")
    if type not in ["movie", "series"]:
        return respond_with({"streams": []}), 400

    # Handle IMDb IDs (starting with 'tt')
    if id.startswith('tt'):
        print("Handling IMDb ID")
        streams = [
            {
                "name": "VidSrc (To)",
                "description": "Stream via VidSrc (To) using IMDb ID",
                "url": f"https://vidsrc.to/embed/movie/{id}",
                "behaviorHints": {"notWebReady": True}
            },
            {
                "name": "VidLink",
                "description": "Stream via VidLink using IMDb ID",
                "url": f"https://vidlink.pro/movie/{id}?primaryColor=9fd829&secondaryColor=9fd829&iconColor=9fd829",
                "behaviorHints": {"notWebReady": True}
            }
        ]
        return respond_with({"streams": streams})

    # Handle TMDb IDs (numeric)
    elif id.isdigit():
        print("Handling TMDb ID")
        streams = [
            {
                "name": "VidSrc (Pro)",
                "description": "Stream via VidSrc (Pro) using TMDb ID",
                "url": f"https://vidsrc.pro/embed/movie/{id}",
                "behaviorHints": {"notWebReady": True}
            },
            {
                "name": "VidSrc (XYZ)",
                "description": "Stream via VidSrc (XYZ) using TMDb ID",
                "url": f"https://vidsrc.xyz/embed/movie/{id}",
                "behaviorHints": {"notWebReady": True}
            },
            {
                "name": "VidLink",
                "description": "Stream via VidLink using TMDb ID",
                "url": f"https://vidlink.pro/movie/{id}?primaryColor=9fd829&secondaryColor=9fd829&iconColor=9fd829",
                "behaviorHints": {"notWebReady": True}
            }
        ]
        return respond_with({"streams": streams})

    # Handle FMovies-style IDs (starting with 'fm_')
    elif id.startswith('fm_'):
        print("Handling FMovies-style ID")
        streams = get_streams(id)
        if not streams:
            print("No streams found for FMovies-style ID")
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

    # Handle direct movie names (fallback to FMovies)
    else:
        print("Handling direct movie name")
        streams = get_streams(f"fm_{id}")
        if not streams:
            print("No streams found for direct movie name")
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
    if type not in ["movie", "series"]:
        return respond_with({"meta": {}}), 400
    
    # Handle IMDb IDs (starting with 'tt')
    if id.startswith('tt'):
        # Fetch metadata for IMDb ID (placeholder logic)
        return respond_with({
            "meta": {
                "id": id,
                "type": type,
                "name": "Movie Title (IMDb)",
                "description": "Description for IMDb-based movie.",
                "poster": "https://example.com/poster.jpg",
                "year": "2023",
                "genres": ["Action", "Drama"],
                "director": "Director Name",
                "cast": ["Actor 1", "Actor 2"]
            }
        })
    
    # Handle TMDb IDs (numeric)
    elif id.isdigit():
        # Fetch metadata for TMDb ID (placeholder logic)
        return respond_with({
            "meta": {
                "id": id,
                "type": type,
                "name": "Movie Title (TMDb)",
                "description": "Description for TMDb-based movie.",
                "poster": "https://example.com/poster.jpg",
                "year": "2023",
                "genres": ["Action", "Drama"],
                "director": "Director Name",
                "cast": ["Actor 1", "Actor 2"]
            }
        })
    
    # Handle FMovies IDs (starting with 'fm_')
    elif id.startswith('fm_'):
        content_id = id.replace('fm_', '').strip('/')
        url = f"https://fmovies24.one/{content_id}"
        
        try:
            print(f"Fetching meta for URL: {url}")
            response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
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
    
    # Handle direct movie names (fallback to FMovies)
    else:
        content_id = id.strip('/')
        url = f"https://fmovies24.one/{content_id}"
        
        try:
            print(f"Fetching meta for URL: {url}")
            response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
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

@app.route('/logo.jpg')
def serve_logo():
    try:
        return send_file('logo.jpg', mimetype='image/jpeg')
    except FileNotFoundError:
        return "Logo not found", 404
        
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8001, debug=False)
