from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import os

from analyzers.python_analyzer import PythonAnalyzer
from analyzers.c_analyzer import CAnalyzer
from analyzers.cpp_analyzer import CppAnalyzer
from analyzers.java_analyzer import JavaAnalyzer
from analyzers.javascript_analyzer import JavaScriptAnalyzer

app = Flask(__name__)
CORS(app)  
analyzers = {
    'python': PythonAnalyzer(),
    'c': CAnalyzer(),
    'cpp': CppAnalyzer(),
    'java': JavaAnalyzer(),
    'javascript': JavaScriptAnalyzer()
}

@app.route('/')
def index():
    """Serve the main HTML page"""
    return render_template('index.html')

@app.route('/api/analyze', methods=['POST'])
def analyze_code():
    """
    API endpoint to analyze code
    Expects JSON: { "code": "...", "language": "python/c/cpp/java/javascript" }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'error': 'No data provided'
            }), 400
        
        code = data.get('code', '').strip()
        language = data.get('language', '').lower().strip()
        
        if not code:
            return jsonify({
                'error': 'No code provided'
            }), 400
        
        if not language:
            return jsonify({
                'error': 'No language specified'
            }), 400
        
        if language not in analyzers:
            return jsonify({
                'error': f'Unsupported language: {language}. Supported: python, c, cpp, java, javascript'
            }), 400
        
        analyzer = analyzers[language]
        results = analyzer.analyze(code)
        
        results['metadata'] = {
            'language': language,
            'lines_of_code': len(code.split('\n')),
            'characters': len(code)
        }
        
        return jsonify(results), 200
        
    except Exception as e:
        return jsonify({
            'error': f'Server error: {str(e)}'
        }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'message': 'Zero-Touch Code Analyzer is running',
        'supported_languages': list(analyzers.keys())
    }), 200

@app.route('/api/languages', methods=['GET'])
def get_languages():
    """Get list of supported languages"""
    return jsonify({
        'languages': [
            {'value': 'python', 'label': 'Python'},
            {'value': 'c', 'label': 'C'},
            {'value': 'cpp', 'label': 'C++'},
            {'value': 'java', 'label': 'Java'},
            {'value': 'javascript', 'label': 'JavaScript'}
        ]
    }), 200

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
