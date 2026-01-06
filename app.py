from flask import Flask 
from prometheus_client import generate_latest, Counter 
import os 
app = Flask(__name__) 
VIEW_COUNT = Counter('total_site_visits', 'Number of visits') 
@app.route('/') 
def hello(): 
    VIEW_COUNT.inc() 
    return "Zero Touch Pipeline: Monitoring Active" 
@app.route('/metrics') 
def metrics(): 
    return generate_latest() 
if __name__ == '__main__': 
    port = int(os.environ.get('PORT', 5000)) 
    app.run(host='0.0.0.0', port=port) 
