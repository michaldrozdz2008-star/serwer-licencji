from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# DANE Z TWOJEGO GISTA
GIST_ID = "218d1eafebaabc1a5b54b69f64a61a2b"
GITHUB_TOKEN = "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"

@app.route('/')
def home():
    return "Serwer Dziala! Uzyj /check do licencji."

@app.route('/check', methods=['POST'])
def check_key():
    try:
        user_data = request.json
        user_key = user_data.get("key")
        
        headers = {"Authorization": f"token {GITHUB_TOKEN}"}
        r = requests.get(f"https://api.github.com/gists/{GIST_ID}", headers=headers, timeout=10)
        
        if r.status_code != 200:
            return jsonify({"status": "error", "message": "BŁĄD GITHUB"}), 500
            
        content = r.json()['files']['keys.txt']['content']
        
        for line in content.strip().split('\n'):
            if "|" in line:
                db_key, db_date = line.split("|")
                if db_key.strip() == user_key.strip():
                    if db_date.strip() == "BANNED":
                        return jsonify({"status": "error", "message": "ZBANOWANY"}), 403
                    return jsonify({"status": "ok", "days": db_date.strip()})
        
        return jsonify({"status": "error", "message": "ZŁY KLUCZ"}), 401
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run()
