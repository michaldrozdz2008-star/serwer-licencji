from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# --- KONFIGURACJA BAZY (Tylko na serwerze) ---
# Tych danych użytkownik cleanera NIE widzi. Są bezpieczne.
GIST_ID = "218d1eafebaabc1a5b54b69f64a61a2b"
GITHUB_TOKEN = "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"

@app.route('/check', methods=['POST'])
def check_key():
    try:
        user_data = request.json
        user_key = user_data.get("key")
        
        # Pobieranie bazy kluczy bezpośrednio z Gista (Serwer używa tokena)
        headers = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}
        r = requests.get(f"https://api.github.com/gists/{GIST_ID}", headers=headers, timeout=10)
        
        # Jeśli GitHub nie odpowie
        if r.status_code != 200:
            return jsonify({"status": "error", "message": "GITHUB API ERROR"}), 500
        
        # Czytanie bazy
        content = r.json()['files']['keys.txt']['content']
        
        found = False
        expires_in = "LFT" # Default
        
        # Weryfikacja klucza
        for line in content.strip().split('\n'):
            if "|" in line:
                db_key, db_date = line.split("|")
                if db_key.strip() == user_key.strip():
                    if db_date.strip() == "BANNED":
                        return jsonify({"status": "error", "message": "YOU ARE BANNED"}), 403
                    
                    found = True
                    # Obliczanie dni (lub Lifetime)
                    if db_date.strip() == "2099-12-31":
                        expires_in = "LFT"
                    else:
                        expires_in = db_date.strip()
                    break
        
        if found:
            return jsonify({"status": "ok", "days": expires_in}), 200
        else:
            return jsonify({"status": "error", "message": "INVALID LICENSE KEY"}), 401
            
    except Exception as e:
        return jsonify({"status": "error", "message": "INTERNAL SERVER ERROR"}), 500

if __name__ == '__main__':
    # Start serwera lokalnie (niepotrzebne na hostingu, ale do testów tak)
    app.run(host='0.0.0.0', port=5000)
