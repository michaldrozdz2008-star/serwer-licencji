from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# --- KONFIGURACJA ---
GIST_ID = "218d1eafebaabc1a5b54b69f64a61a2b"
# Twój nowy token
GITHUB_TOKEN = "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"

@app.route('/')
def home():
    return "Serwer Dziala! Uzyj /check do licencji."

@app.route('/check', methods=['POST'])
def check_key():
    try:
        user_data = request.json
        if not user_data:
            return jsonify({"status": "error", "message": "BRAK DANYCH"}), 400
            
        user_key = user_data.get("key")
        
        # Pobieranie bazy kluczy z Gista
        headers = {"Authorization": f"token {GITHUB_TOKEN}"}
        r = requests.get(f"https://api.github.com/gists/{GIST_ID}", headers=headers, timeout=10)
        
        if r.status_code != 200:
            return jsonify({"status": "error", "message": "BLAD GITHUB API (TOKEN?)"}), 500
            
        files = r.json().get('files', {})
        if 'keys.txt' not in files:
            return jsonify({"status": "error", "message": "BRAK PLIKU KEYS.TXT"}), 500
            
        content = files['keys.txt']['content']
        
        # Sprawdzanie klucza w tekście
        for line in content.strip().split('\n'):
            if "|" in line:
                db_key, db_date = line.split("|")
                if db_key.strip() == user_key.strip():
                    # Sprawdzanie bana
                    if db_date.strip().upper() == "BANNED":
                        return jsonify({"status": "error", "message": "ZBANOWANY"}), 403
                    
                    # Jeśli klucz pasuje, zwracamy OK i datę
                    return jsonify({"status": "ok", "days": db_date.strip()})
        
        return jsonify({"status": "error", "message": "ZLY KLUCZ"}), 401
        
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run()
