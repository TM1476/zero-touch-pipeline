from flask import Flask, render_template_string
from prometheus_client import generate_latest, Counter
import os
app = Flask(__name__)
VIEW_COUNT = Counter('total_site_visits', 'Number of visits')
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Zero-Touch Pipeline Dashboard</title>
    <style>
        body { font-family: Arial, sans-serif; text-align: center; background-color: #f4f4f9; padding: 50px; }
        .card { background: white; padding: 30px; border-radius: 15px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); display: inline-block; }
        h1 { color: #2c3e50; }
        .btn { background: #3498db; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; }
        .status { color: #27ae60; font-weight: bold; }
    </style>
</head>
<body>
    <div class="card">
        <h1>?? Zero-Touch Pipeline</h1>
        <p>Status: <span class="status">LIVE & MONITORING</span></p>
        <hr>
        <p>This project uses <b>Docker</b>, <b>GitHub Actions</b>, and <b>Prometheus</b>.</p>
        <br>
        <a href="/metrics" class="btn">View Raw Metrics Data</a>
    </div>
</body>
</html>
"""
@app.route('/')
def hello():
    VIEW_COUNT.inc()
    return render_template_string(HTML_TEMPLATE)
@app.route('/metrics')
def metrics():
    return generate_latest()
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
