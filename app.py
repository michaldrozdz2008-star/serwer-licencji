from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# LINK RAW DO TWOJEGO GISTA Z KLUCZAMI
GIST_URL = "https://gist.githubusercontent.com/michaldrozdz2008-star/218d1eafebaabc1a5b54b69f64a61a2b/raw/keys.txt"

def get_remote_keys():
    try:
        response = requests.get(GIST_URL)
        lines = [line.strip() for line in response.text.split('\n') if line.strip()]
        keys_db = {}
        for line in lines:
            if "|" in line:
                key, expiry = line.split('|')
                keys_db[key.strip()] = expiry.strip()
        return keys_db
    except:
        return {}

@app.route("/check", methods=["POST"])
def check():
    data = request.json
    user_key = data.get("key")
    valid_keys = get_remote_keys()
    
    if user_key in valid_keys:
        return jsonify({"status": "ok", "message": "Access Granted"})
    return jsonify({"status": "error", "message": "INVALID KEY!"})

if __name__ == "__main__":
    app.run()
