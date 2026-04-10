import os
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Twoje stałe dane
GIST_ID = "218d1eafebaabc1a5b54b69f64a61a2b"
# Pobieranie tokena z Environment Variables (bezpieczne)
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")

@app.route('/')
def home():
    return "Serwer Aktywny"

@app.route('/check', methods=['POST'])
def check_key():
    try:
        data = request.json
        user_key = data.get("key")
        
        headers = {"Authorization": f"token {GITHUB_TOKEN}"}
        r = requests.get(f"https://api.github.com/gists/{GIST_ID}", headers=headers)
        
        if r.status_code != 200:
            return jsonify({"status": "error", "message": "Problem z autoryzacją serwera"}), 500
            
        content = r.json()['files']['keys.txt']['content']
        for line in content.strip().split('\n'):
            if "|" in line:
                db_key, db_date = line.split("|")
                if db_key.strip() == user_key.strip():
                    return jsonify({"status": "ok", "days": db_date.strip()})
                    
        return jsonify({"status": "error", "message": "Niepoprawny klucz"}), 401
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
