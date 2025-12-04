#!/usr/bin/env python3
from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename
import os
import json
try:
    import fitz  # PyMuPDF
except Exception:
    fitz = None

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
ALLOWED_EXTENSIONS = {'pdf'}

app = Flask(__name__, static_folder='static', template_folder='templates')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload():
    left = request.files.get('left')
    right = request.files.get('right')
    if not left or not right:
        return 'Please upload two PDF files', 400

    if not allowed_file(left.filename) or not allowed_file(right.filename):
        return 'Only PDF files allowed', 400

    left_name = secure_filename(left.filename)
    right_name = secure_filename(right.filename)

    left_path = os.path.join(app.config['UPLOAD_FOLDER'], left_name)
    right_path = os.path.join(app.config['UPLOAD_FOLDER'], right_name)

    left.save(left_path)
    right.save(right_path)

    return redirect(url_for('viewer', l=left_name, r=right_name))


@app.route('/viewer')
def viewer():
    left = request.args.get('l')
    right = request.args.get('r')
    if not left or not right:
        return redirect(url_for('index'))
    left_url = url_for('uploaded_file', filename=left)
    right_url = url_for('uploaded_file', filename=right)
    return render_template('viewer.html', left_url=left_url, right_url=right_url)


@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


def normalize_text(s: str) -> str:
    # simple normalization: lowercase, keep letters+numbers and spaces
    import re
    # allow hyphen and vertical bar as well (keep them as characters to compare)
    return re.sub(r'[^0-9a-z\-\| ]+', '', s.lower())


@app.route('/textdiff')
def textdiff():
    # returns JSON with normalized boxes for left and right for the given page
    if fitz is None:
        return {'error': 'PyMuPDF not installed on server'}, 500
    left_name = request.args.get('l')
    right_name = request.args.get('r')
    page = int(request.args.get('page', '1'))
    if not left_name or not right_name:
        return {'error': 'missing filenames'}, 400

    left_path = os.path.join(app.config['UPLOAD_FOLDER'], left_name)
    right_path = os.path.join(app.config['UPLOAD_FOLDER'], right_name)
    if not os.path.exists(left_path) or not os.path.exists(right_path):
        return {'error': 'file not found'}, 404

    def extract_words(path, page_num):
        doc = fitz.open(path)
        if page_num < 1 or page_num > doc.page_count:
            return []
        p = doc.load_page(page_num-1)
        # words: list of tuples (x0, y0, x1, y1, word)
        words = p.get_text('words')
        # page size
        rect = p.rect
        pw = rect.width
        ph = rect.height
        items = []
        for w in words:
            x0,y0,x1,y1,text = w[0],w[1],w[2],w[3],w[4]
            tn = normalize_text(text)
            if tn.strip() == '':
                continue
            items.append({
                'text': text,
                'norm': tn,
                'x0': x0/pw,
                'y0': y0/ph,
                'x1': x1/pw,
                'y1': y1/ph,
            })
        return items

    left_words = extract_words(left_path, page)
    right_words = extract_words(right_path, page)

    # compare: for each left word, find matching right word by normalized text and overlap
    def intersects(a,b):
        return not (a['x1'] < b['x0'] or a['x0'] > b['x1'] or a['y1'] < b['y0'] or a['y0'] > b['y1'])

    matched_right = [False]*len(right_words)
    left_boxes = []
    for lw in left_words:
        found = False
        for i,rw in enumerate(right_words):
            if matched_right[i]:
                continue
            if lw['norm'] == rw['norm'] and intersects(lw,rw):
                matched_right[i] = True
                found = True
                break
        if not found:
            left_boxes.append({
                'box': [lw['x0'], lw['y0'], lw['x1'], lw['y1']],
                'text': lw['text'],
                'dashCount': lw['text'].count('-') + lw['text'].count('|')
            })

    right_boxes = []
    matched_left = [False]*len(left_words)
    for i,rw in enumerate(right_words):
        found = False
        for lw in left_words:
            if rw['norm'] == lw['norm'] and intersects(rw,lw):
                found = True
                break
        if not found:
            # only count dashes/pipes if text contains no numbers
            dashCount = 0
            if not any(c.isdigit() for c in rw['text']):
                dashCount = rw['text'].count('-') + rw['text'].count('|')
            right_boxes.append({
                'box': [rw['x0'], rw['y0'], rw['x1'], rw['y1']],
                'text': rw['text'],
                'dashCount': dashCount
            })

    return json.dumps({'left': left_boxes, 'right': right_boxes})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
