from flask import Flask, render_template_string, request
from prometheus_client import generate_latest, Counter
import os
app = Flask(__name__)
VIEW_COUNT = Counter('total_site_visits', 'Number of visits')
ANALYZE_COUNT = Counter('total_analyses', 'Number of times tool was used')
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Zero-Touch Code Analyzer</title>
    <style>
        body { font-family: 'Segoe UI', sans-serif; background-color: #0e1117; color: white; text-align: center; padding: 50px; }
        .container { background: #161b22; padding: 30px; border-radius: 15px; border: 1px solid #30363d; display: inline-block; width: 80%%; max-width: 600px; }
        textarea { width: 100%%; height: 150px; background: #0d1117; color: #58a6ff; border: 1px solid #30363d; border-radius: 5px; padding: 10px; font-family: monospace; }
        .btn { background: #238636; color: white; padding: 10px 20px; border: none; border-radius: 6px; cursor: pointer; margin-top: 15px; font-weight: bold; }
        .result { margin-top: 20px; padding: 15px; background: #21262d; border-radius: 8px; text-align: left; border-left: 4px solid #58a6ff; }
        h1 { color: #58a6ff; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Code Analyzer Tool</h1>
        <p>Paste your code/text below to analyze it using the automated pipeline.</p>
        <form method="POST">
            <textarea name="user_code" placeholder="Paste your code here..."></textarea><br>
            <button type="submit" class="btn">Analyze Code</button>
        </form>
        {% if result %}
        <div class="result">
            <b>Analysis Result:</b><br>
            Line Count: {{ result.lines }}<br>
            Character Count: {{ result.chars }}
        </div>
        {% endif %}
        <br><hr>
        <a href="/metrics" style="color: #8b949e; text-decoration: none; font-size: 12px;">View Backend Metrics</a>
    </div>
</body>
</html>
"""
@app.route('/', methods=['GET', 'POST'])
def home():
    VIEW_COUNT.inc()
    result = None
    if request.method == 'POST':
        ANALYZE_COUNT.inc()
        code = request.form.get('user_code', '')
        result = {'lines': len(code.splitlines()), 'chars': len(code)}
    return render_template_string(HTML_TEMPLATE, result=result)
@app.route('/metrics')
def metrics():
    return generate_latest()
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
