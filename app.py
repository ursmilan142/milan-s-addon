from flask import Flask, jsonify

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
        "id": "com.example.direct-stream-addon",
        "version": "1.0.0",
        "name": "Direct Stream Addon",
        "description": "Stream movies and series using direct video URLs",
        "resources": ["stream"],
        "types": ["movie", "series"],
        "idPrefixes": ["tt"],  # Support IMDb IDs
        "logo": "https://github.com/ursmilan142/milan-s-addon/blob/f33720bbaf4e1d4cb07cdb3c9119abc08038c91f/logo.jpg"
    })

@app.route('/stream/<type>/<id>.json')
def stream(type, id):
    if type not in ["movie", "series"]:
        return respond_with({"streams": []}), 400

    # Handle IMDb IDs (starting with 'tt')
    if id.startswith('tt'):
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

    # Handle unsupported IDs
    return respond_with({"streams": []}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8001, debug=True)
