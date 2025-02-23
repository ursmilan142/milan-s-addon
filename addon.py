from flask import Flask, jsonify, request
import requests
from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.edge.service import Service
import time
import os
import logging

app = Flask(__name__)

# Suppress Selenium logs by setting logging levels
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger('selenium.webdriver.remote.remote_connection')
logger.setLevel(logging.ERROR)

def get_api_key(tmdb_id):
    service = Service(executable_path="C:/EDGE Driver/msedgedriver.exe")
    service.log_output = os.devnull

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--log-level=3")
    options.add_argument("--disable-logging")

    driver = webdriver.Edge(service=service, options=options)
    driver.get(f"https://vidlink.pro/movie/{tmdb_id}")
    time.sleep(5)
    key = driver.execute_script("return window.getAdv(arguments[0]);", tmdb_id)
    driver.quit()
    if key and isinstance(key, str):
        return key.replace(" ", "")
    return key

def parse_master_playlist(m3u8_content):
    lines = m3u8_content.splitlines()
    variants = {}
    for i, line in enumerate(lines):
        if line.startswith("#EXT-X-STREAM-INF"):
            bandwidth = line.split("BANDWIDTH=")[1].split(",")[0]
            resolution = line.split("RESOLUTION=")[1] if "RESOLUTION=" in line else "Unknown"
            url = lines[i + 1]
            variants[resolution] = {"bandwidth": bandwidth, "url": url}
    return variants

@app.route('/get_m3u8_url', methods=['GET'])
def get_m3u8_url():
    tmdb_id = request.args.get('tmdb_id')
    api_key = get_api_key(tmdb_id)
    if not api_key:
        return jsonify({"error": "Failed to retrieve API key"}), 400

    url = f"https://vidlink.pro/api/b/movie/{api_key}?multiLang=0"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36 Edg/134.0.0.0",
        "Referer": f"https://vidlink.pro/movie/{tmdb_id}"
    }
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        master_m3u8_url = data["stream"]["playlist"]

        m3u8_response = requests.get(master_m3u8_url, headers=headers)
        if m3u8_response.status_code == 200:
            variants = parse_master_playlist(m3u8_response.text)
            return jsonify({"master_url": master_m3u8_url, "variants": variants})
        else:
            return jsonify({"error": f"Failed to fetch master playlist: {m3u8_response.status_code}"}), 400
    else:
        return jsonify({"error": f"Failed to fetch stream: {response.status_code}"}), 400

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
