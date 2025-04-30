from flask import Flask, request, jsonify, send_file, render_template
from werkzeug.utils import secure_filename
from io import BytesIO
import requests, docx, PyPDF2, os
from fpdf import FPDF

app = Flask(__name__,
            static_folder='static',      # serve CSS/JS from ./static
            template_folder='templates') # look for index.html in ./templates

# <-- point this at your LibreTranslate endpoint (or public instance) -->
LIBRE_URL = "http://127.0.0.1:5001/translate"


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/translate', methods=['POST'])
def translate_text():
    data = request.get_json()
    text   = data.get('text', '')
    source = data.get('source', 'auto')
    target = data.get('target', 'en')

    # call LibreTranslate
    resp = requests.post(LIBRE_URL, json={
        'q': text,
        'source': source,
        'target': target,
        'format': 'text'
    })
    resp.raise_for_status()
    translated = resp.json().get('translatedText', '')

    return jsonify({ 'translatedText': translated })


@app.route('/upload', methods=['POST'])
def translate_file():
    file   = request.files.get('file')
    source = request.form.get('source', 'auto')
    target = request.form.get('target', 'en')
    if not file:
        return jsonify({'error':'no file'}), 400

    filename = secure_filename(file.filename)
    ext = os.path.splitext(filename)[1].lower()

    # 1) Extract plain text
    if ext == '.txt':
        raw = file.read().decode('utf-8')
    elif ext == '.docx':
        doc = docx.Document(file)
        raw = '\n'.join([p.text for p in doc.paragraphs])
    elif ext == '.pdf':
        reader = PyPDF2.PdfReader(file)
        raw = ''.join(page.extract_text() + '\n' for page in reader.pages)
    else:
        return jsonify({'error':'unsupported'}), 400

    # 2) Translate
    resp = requests.post(LIBRE_URL, json={
        'q': raw,
        'source': source,
        'target': target,
        'format': 'text'
    })
    resp.raise_for_status()
    translated = resp.json().get('translatedText','')

    # 3) Return file
    mem = BytesIO()
    if ext == '.pdf':
        pdf = FPDF()
        pdf.add_page()
        pdf.set_auto_page_break(True, margin=15)
        pdf.set_font('Arial', size=12)
        for line in translated.split('\n'):
            pdf.multi_cell(0, 8, line)
        pdf.output(mem)
        mimetype='application/pdf'

    elif ext == '.docx':
        new = docx.Document()
        for line in translated.split('\n'):
            new.add_paragraph(line)
        new.save(mem)
        mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document'

    else:  # .txt
        mem.write(translated.encode('utf-8'))
        mimetype='text/plain'

    mem.seek(0)
    return send_file(mem,
                     as_attachment=True,
                     download_name=f'translated_{filename}',
                     mimetype=mimetype)


if __name__ == '__main__':
    app.run(debug=True)
