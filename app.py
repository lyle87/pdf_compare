#!/usr/bin/env python3
from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import os
import sys
import json
try:
    import fitz  # PyMuPDF
except Exception:
    fitz = None

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def _resource_root() -> str:
    """Return the folder that contains bundled templates/static assets."""

    if getattr(sys, "frozen", False):
        # PyInstaller onefile/unpacked builds expose bundled assets in _MEIPASS
        return getattr(sys, "_MEIPASS", BASE_DIR)
    return BASE_DIR


def _runtime_root() -> str:
    """Return the folder where runtime artifacts (uploads) should live."""

    if getattr(sys, "frozen", False):
        # When frozen, keep uploads beside the .exe so the app stays portable
        return os.path.dirname(sys.executable)
    return BASE_DIR


RESOURCE_ROOT = _resource_root()
RUNTIME_ROOT = _runtime_root()
UPLOAD_FOLDER = os.path.join(RUNTIME_ROOT, "uploads")
ALLOWED_EXTENSIONS = {'pdf'}

app = Flask(
    __name__,
    static_folder=os.path.join(RESOURCE_ROOT, "static"),
    template_folder=os.path.join(RESOURCE_ROOT, "templates"),
)
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


@app.route('/cmm', methods=['GET'])
def cmm():
    return render_template('cmm.html', part_types=["675", "50TT", "50TL"])


def normalize_text(s: str) -> str:
    # simple normalization: lowercase, keep letters+numbers and spaces
    import re
    # allow hyphen and vertical bar as well (keep them as characters to compare)
    return re.sub(r'[^0-9a-z\-\| ]+', '', s.lower())


def _is_numeric_token(token: str) -> bool:
    import re
    # A numeric column token must be strictly numeric (no letters),
    # optionally comma-separated and with an optional decimal part.
    # Examples: 10, -10.25, 1,234.50
    return re.match(r'^[+-]?\d[\d,]*(\.\d+)?$', token) is not None


def _parse_numeric_token(token: str) -> Optional[float]:
    """Return float value for token that may contain commas; otherwise None."""

    try:
        cleaned = token.replace(",", "")
        return float(cleaned)
    except Exception:
        return None


def _extract_cmm_rows(path: str) -> List[Tuple[str, float]]:
    """
    Extract ZEISS CMM feature rows with support for:
    - Standard single-line features
    - POS X-Y-Z multi-line features → converted into separate X, Y, Z features.
    """

    if fitz is None:
        raise RuntimeError("PyMuPDF is required to parse CMM reports")

    rows: List[Tuple[str, float]] = []
    doc = fitz.open(path)

    for page in doc:
        words = page.get_text("words")
        if not words:
            continue

        # Locate header columns
        actual_x = deviation_x = hist_x = None

        for x0, y0, x1, y1, text, *_ in words:
            if text == "Actual":
                actual_x = x0
            elif text == "Deviation":
                deviation_x = x0
            elif text == "Histogram":
                hist_x = x0

        if actual_x is None or deviation_x is None or hist_x is None:
            continue

        feature_limit_x = actual_x - 5
        deviation_min_x = deviation_x - 5
        deviation_max_x = hist_x + 5

        # Convert to row clusters by Y
        items = []
        for (x0, y0, x1, y1, text, *_) in words:
            y_center = (y0 + y1) / 2
            items.append({"x": x0, "y": y_center, "text": text})

        items.sort(key=lambda w: (w["y"], w["x"]))

        row_groups = []
        current = []
        last_y = None

        for w in items:
            if last_y is None or abs(w["y"] - last_y) <= 1.0:
                current.append(w)
            else:
                row_groups.append(current)
                current = [w]
            last_y = w["y"]

        if current:
            row_groups.append(current)

        # Parent state
        current_parent_feature = None

        def parse_axis_row(text):
            return text in ("X", "Y", "Z")

        for group in row_groups:
            feature_tokens = []
            deviation_candidates = []
            axis_row_label = None

            # Detect axis-only child rows
            for w in group:
                if parse_axis_row(w["text"].strip()):
                    axis_row_label = w["text"].strip()

            # Handle axis child rows → create separate features
            if axis_row_label and current_parent_feature:
                # collect deviation number
                dev_val = None
                for w in group:
                    tx = w["text"].strip()
                    if _is_numeric_token(tx) and deviation_min_x <= w["x"] < deviation_max_x:
                        dev_val = _parse_numeric_token(tx)

                if dev_val is not None:
                    # Example: H203 POS X
                    feature_full = f"{current_parent_feature} {axis_row_label}"
                    rows.append((feature_full, dev_val))

                continue

            # Otherwise, process normally (parent row or single-line feature)
            for w in group:
                tx = w["text"].strip()
                x = w["x"]

                if x < feature_limit_x:
                    feature_tokens.append(tx)
                else:
                    if _is_numeric_token(tx) and deviation_min_x <= x < deviation_max_x:
                        deviation_candidates.append(tx)

            feature_name = " ".join(feature_tokens).strip()

            if not feature_name or not any(c.isalpha() for c in feature_name):
                continue

            lname = feature_name.lower()
            if (
                "plan name" in lname or
                "part serial" in lname or
                lname.startswith("date") or
                "histogram" in lname or
                "nominal" in lname or
                "actual" in lname
            ):
                continue

            # Detect POS X-Y-Z multi-parent row
            if "pos x-y-z" in lname or "pos x-y-z" in lname:
                current_parent_feature = feature_name.replace("X-Y-Z", "").strip()
                continue

            # Normal single-line feature
            current_parent_feature = None

            if deviation_candidates:
                deviation_value = _parse_numeric_token(deviation_candidates[-1])
                rows.append((feature_name, deviation_value))

    return rows






def _collect_cmm_data(
    folder: str,
    start_date: Optional[datetime],
    end_date: Optional[datetime],
    part_type: Optional[str],
    errors: Optional[List[str]] = None,
) -> Dict[str, List[Dict[str, object]]]:
    """Scan PDFs in *folder* and return feature deviations keyed by feature name."""

    results: Dict[str, List[Dict[str, object]]] = {}
    part_type_upper = part_type.upper() if part_type else None

    for entry in sorted(os.listdir(folder)):
        if not entry.lower().endswith('.pdf'):
            continue

        full_path = os.path.join(folder, entry)
        if not os.path.isfile(full_path):
            continue

        if part_type_upper and part_type_upper not in entry.upper():
            continue

        mtime = datetime.fromtimestamp(os.path.getmtime(full_path))
        if start_date and mtime < start_date:
            continue
        if end_date and mtime > end_date:
            continue

        try:
            rows = _extract_cmm_rows(full_path)
        except Exception as exc:
            if errors is not None:
                errors.append(f"{entry}: {exc}")
            continue

        for feature, deviation in rows:
            results.setdefault(feature, []).append({
                'date': mtime.isoformat(),
                'deviation': deviation,
                'report': entry,
            })

    for feature in results:
        results[feature].sort(key=lambda r: r['date'])

    return results


def _parse_date(date_str: Optional[str]) -> Optional[datetime]:
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        return None


@app.route('/api/cmm_summary', methods=['POST'])
def cmm_summary():
    payload = request.get_json(silent=True) or {}
    folder = payload.get('folder')
    part_type = payload.get('partType')
    start_date = _parse_date(payload.get('startDate'))
    end_date = _parse_date(payload.get('endDate'))

    if not folder:
        return {'error': 'Missing folder path'}, 400
    if not os.path.isdir(folder):
        return {'error': f'Folder does not exist: {folder}'}, 400
    if fitz is None:
        return {'error': 'PyMuPDF is required to parse CMM reports'}, 500

    errors: List[str] = []
    data = _collect_cmm_data(folder, start_date, end_date, part_type, errors)

    features = []
    report_names = set()
    for name in sorted(data.keys()):
        points = data[name]
        for p in points:
            report_names.add(p['report'])
        latest = points[-1]['deviation'] if points else None
        features.append({
            'name': name,
            'latest': latest,
            'points': points,
        })

    response = {
        'features': features,
        'reportsAnalyzed': len(report_names),
        'errors': errors,
    }
    return json.dumps(response)


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

    def deviation_score(text: str) -> int:
        """Return a simple deviation metric for strings like "--|".

        A lower score indicates a value closer to nominal. Ignore numbers so
        regular values aren't treated as deviation markers.
        """

        if any(c.isdigit() for c in text):
            return -1
        if '-' not in text and '|' not in text:
            return -1
        return text.count('-')

    def dash_metric(text: str) -> int:
        """Return the dash count used for coloring overlays."""

        if any(c.isdigit() for c in text):
            return 0
        return text.count('-') + text.count('|')

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
                'dashCount': dash_metric(lw['text'])
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
            dashCount = dash_metric(rw['text'])
            deviation = deviation_score(rw['text'])
            improved = False
            if deviation >= 0 and '|' in rw['text']:
                for lw in left_words:
                    left_deviation = deviation_score(lw['text'])
                    if left_deviation < 0:
                        continue
                    if rw['text'].count('|') != lw['text'].count('|'):
                        continue
                    if not intersects(rw, lw):
                        continue
                    if deviation < left_deviation:
                        improved = True
                        break
            right_boxes.append({
                'box': [rw['x0'], rw['y0'], rw['x1'], rw['y1']],
                'text': rw['text'],
                'dashCount': dashCount,
                'improved': improved
            })

    return json.dumps({'left': left_boxes, 'right': right_boxes})


def _find_free_port(host: str) -> int:
    """Return an available port bound to the provided host."""
    import socket

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host, 0))
        return s.getsockname()[1]


def _pick_listen_address(host_hint: Optional[str], port_hint: Optional[str]):
    """Choose a listen host/port that we can bind to."""

    import socket

    default_host = "127.0.0.1" if os.name == "nt" else "0.0.0.0"
    host = host_hint or default_host
    port = int(port_hint or "5000")

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
            probe.bind((host, port))
    except OSError as exc:
        errno = getattr(exc, "errno", None)
        # Permission denied / address in use / access errors
        if errno not in {13, 48, 98, 10013}:
            raise

        fallback_host = "127.0.0.1"
        fallback_port = _find_free_port(fallback_host)
        note = (
            f"Port {port} on {host} is unavailable or requires elevated permissions. "
            f"Switching to http://{fallback_host}:{fallback_port} instead."
        )
        return fallback_host, fallback_port, note

    return host, port, None


def _auto_launch_browser(host: str, port: int):
    import threading
    import webbrowser

    def _open():
        webbrowser.open(f"http://{host}:{port}", new=2, autoraise=True)

    threading.Timer(1.0, _open).start()


def _run_app():
    # Default to a localhost-only host on Windows to avoid corporate socket restrictions
    host_hint = os.environ.get("PDF_COMPARE_HOST")
    port_hint = os.environ.get("PDF_COMPARE_PORT")

    host, port, note = _pick_listen_address(host_hint, port_hint)
    if note:
        print("\n" + note + "\n")

    _auto_launch_browser(host, port)
    app.run(host=host, port=port, debug=True, use_reloader=False)


if __name__ == '__main__':
    _run_app()
