import os
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Twoje stałe dane
GIST_ID = "218d1eafebaabc1a5b54b69f64a61a2b"
# To pobierze token z zakładki Environment na Renderze
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")

@app.route('/')
def home():
    return "Serwer Aktywny! Baza kluczy polaczona."

@app.route('/check', methods=['POST'])
def check_key():
    try:
        data = request.json
        if not data:
            return jsonify({"status": "error", "message": "Brak danych wejsciowych"}), 400
            
        user_key = data.get("key")
        
        headers = {"Authorization": f"token {GITHUB_TOKEN}"}
        r = requests.get(f"https://api.github.com/gists/{GIST_ID}", headers=headers, timeout=10)
        
        if r.status_code != 200:
            return jsonify({"status": "error", "message": f"Serwer nie ma dostępu do bazy (Kod: {r.status_code})"}), 500
            
        content = r.json()['files']['keys.txt']['content']
        
        # Przeszukiwanie bazy
        for line in content.strip().split('\n'):
            if "|" in line:
                db_key, db_date = line.split("|")
                if db_key.strip() == user_key.strip():
                    if db_date.strip().upper() == "BANNED":
                        return jsonify({"status": "error", "message": "Klucz zablokowany!"}), 403
                    return jsonify({"status": "ok", "days": db_date.strip()})
                    
        return jsonify({"status": "error", "message": "Niepoprawny klucz"}), 401
        
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run()
