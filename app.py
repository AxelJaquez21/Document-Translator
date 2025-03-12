from flask import Flask, request, jsonify, render_template, send_from_directory
from googletrans import Translator
import os

app = Flask(__name__)
translator = Translator()

@app.route('/')
def home():
    return render_template('index.html')

# Manually serve static files if necessary
@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory(os.path.join(app.root_path, 'static'), filename)

@app.route('/translate', methods=['POST'])
def translate():
    try:
        data = request.get_json()
        text = data.get("text", "")
        source = data.get("source", "auto")
        target = data.get("target", "en")
        
        if not text:
            return jsonify({"error": "No text provided for translation."}), 400
        
        translated = translator.translate(text, src=source, dest=target)
        return jsonify({"translated_text": translated.text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)