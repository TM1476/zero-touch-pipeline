import ast
import pylint.lint
from pylint.reporters.text import TextReporter
import io
import sys
import traceback

class PythonAnalyzer:
    def __init__(self):
        self.name = "Python Analyzer"
    
    def analyze(self, code):
        """Analyze Python code for bugs and issues"""
        results = {
            'language': 'Python',
            'bugs': [],
            'warnings': [],
            'suggestions': [],
            'score': 0
        }
        
        try:
            try:
                ast.parse(code)
                results['suggestions'].append({
                    'type': 'success',
                    'message': 'Code syntax is valid',
                    'line': 0
                })
            except SyntaxError as e:
                results['bugs'].append({
                    'type': 'Syntax Error',
                    'line': e.lineno if e.lineno else 0,
                    'message': str(e.msg),
                    'suggestion': f'Fix syntax error at line {e.lineno}: {e.msg}'
                })
                return results  
            
            pylint_output = io.StringIO()
            reporter = TextReporter(pylint_output)
            
            from pylint.lint import Run
            
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(code)
                temp_file = f.name
            
            try:
                Run([temp_file, '--disable=C0111,C0103'], reporter=reporter, exit=False)
                
                pylint_result = pylint_output.getvalue()
                
                for line in pylint_result.split('\n'):
                    if ':' in line and any(x in line for x in ['error', 'warning', 'convention', 'refactor']):
                        parts = line.split(':')
                        if len(parts) >= 3:
                            try:
                                line_num = int(parts[1].strip())
                                message = ':'.join(parts[2:]).strip()
                                
                                if 'error' in line.lower():
                                    results['bugs'].append({
                                        'type': 'Error',
                                        'line': line_num,
                                        'message': message,
                                        'suggestion': self.get_suggestion(message)
                                    })
                                else:
                                    results['warnings'].append({
                                        'type': 'Warning',
                                        'line': line_num,
                                        'message': message,
                                        'suggestion': self.get_suggestion(message)
                                    })
                            except (ValueError, IndexError):
                                continue
              
                total_issues = len(results['bugs']) + len(results['warnings'])
                if total_issues == 0:
                    results['score'] = 100
                else:
                    results['score'] = max(0, 100 - (total_issues * 5))
                
            finally:
                import os
                if os.path.exists(temp_file):
                    os.remove(temp_file)

            self.check_common_issues(code, results)
            
        except Exception as e:
            results['bugs'].append({
                'type': 'Analysis Error',
                'line': 0,
                'message': f'Error during analysis: {str(e)}',
                'suggestion': 'Please check your code for unusual patterns'
            })
        
        return results
    
    def check_common_issues(self, code, results):
        """Check for common Python coding issues"""
        lines = code.split('\n')
        
        for i, line in enumerate(lines, 1):
            if '=' in line and not line.strip().startswith('#'):
                if 'import' not in line:
                    var_name = line.split('=')[0].strip().split()[-1]
                    if var_name and not any(var_name in other_line for j, other_line in enumerate(lines) if j != i-1):
                        results['warnings'].append({
                            'type': 'Unused Variable',
                            'line': i,
                            'message': f'Variable "{var_name}" might be unused',
                            'suggestion': f'Consider removing or using variable "{var_name}"'
                        })
            
            if 'print(' in line and not line.strip().startswith('#'):
                results['warnings'].append({
                    'type': 'Debug Code',
                    'line': i,
                    'message': 'Print statement found (possible debug code)',
                    'suggestion': 'Consider using logging instead of print statements'
                })
    
    def get_suggestion(self, message):
        """Generate fix suggestions based on error message"""
        suggestions = {
            'undefined': 'Make sure the variable is defined before using it',
            'import': 'Check if the module is installed and imported correctly',
            'indent': 'Fix indentation - Python uses 4 spaces per indent level',
            'syntax': 'Check for missing colons, parentheses, or quotes',
            'name': 'Check variable spelling and make sure it is defined',
            'type': 'Verify you are using the correct data type for this operation',
            'attribute': 'Check if the object has this attribute/method',
            'index': 'Make sure the index is within the list/string range',
            'key': 'Verify the dictionary key exists',
            'zero': 'Add a check to prevent division by zero'
        }
        
        message_lower = message.lower()
        for key, suggestion in suggestions.items():
            if key in message_lower:
                return suggestion
        
        return 'Review the code logic and fix the issue'
