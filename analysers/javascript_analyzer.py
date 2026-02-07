import re
import json

class JavaScriptAnalyzer:
    def __init__(self):
        self.name = "JavaScript Analyzer"
    
    def analyze(self, code):
        """Analyze JavaScript code for bugs and issues"""
        results = {
            'language': 'JavaScript',
            'bugs': [],
            'warnings': [],
            'suggestions': [],
            'score': 0
        }
        
        try:
            lines = code.split('\n')
            
            self.check_syntax(lines, results)
            
            self.check_common_issues(lines, results)
            
            self.check_modern_practices(lines, results)
            
            total_issues = len(results['bugs']) + len(results['warnings'])
            if total_issues == 0:
                results['score'] = 100
                results['suggestions'].append({
                    'type': 'success',
                    'message': 'No major issues found in JavaScript code',
                    'line': 0
                })
            else:
                results['score'] = max(0, 100 - (total_issues * 5))
            
        except Exception as e:
            results['bugs'].append({
                'type': 'Analysis Error',
                'line': 0,
                'message': f'Error during analysis: {str(e)}',
                'suggestion': 'Please check your code structure'
            })
        
        return results
    
    def check_syntax(self, lines, results):
        """Check for basic JavaScript syntax issues"""
        brace_count = 0
        paren_count = 0
        bracket_count = 0
        
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            
            if stripped.startswith('//') or stripped.startswith('/*') or not stripped:
                continue
            
            brace_count += stripped.count('{') - stripped.count('}')
            paren_count += stripped.count('(') - stripped.count(')')
            bracket_count += stripped.count('[') - stripped.count(']')
            
            if any(keyword in stripped for keyword in ['var ', 'let ', 'const ', 'return ']):
                if not stripped.endswith(';') and not stripped.endswith('{') and not stripped.endswith(','):
                    if not any(x in stripped for x in ['function', 'if', 'for', 'while', '=>']):
                        results['warnings'].append({
                            'type': 'Style Warning',
                            'line': i,
                            'message': 'Missing semicolon (optional in JS but recommended)',
                            'suggestion': 'Add semicolon for consistency and to avoid ASI issues'
                        })
        
        if brace_count != 0:
            results['bugs'].append({
                'type': 'Syntax Error',
                'line': 0,
                'message': 'Unbalanced curly braces',
                'suggestion': f'Check your curly braces - {abs(brace_count)} brace(s) unmatched'
            })
        
        if paren_count != 0:
            results['bugs'].append({
                'type': 'Syntax Error',
                'line': 0,
                'message': 'Unbalanced parentheses',
                'suggestion': f'Check your parentheses - {abs(paren_count)} parenthesis unmatched'
            })
        
        if bracket_count != 0:
            results['bugs'].append({
                'type': 'Syntax Error',
                'line': 0,
                'message': 'Unbalanced square brackets',
                'suggestion': f'Check your square brackets - {abs(bracket_count)} bracket(s) unmatched'
            })
    
    def check_common_issues(self, lines, results):
        """Check for common JavaScript issues"""
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            
            if ' == ' in stripped or ' != ' in stripped:
                if '===' not in stripped and '!==' not in stripped:
                    results['warnings'].append({
                        'type': 'Comparison Warning',
                        'line': i,
                        'message': 'Using == or != instead of === or !==',
                        'suggestion': 'Use === and !== for strict equality comparison to avoid type coercion'
                    })
            
            if 'var ' in stripped:
                results['warnings'].append({
                    'type': 'Modern JS',
                    'line': i,
                    'message': 'Using var keyword',
                    'suggestion': 'Use let or const instead of var for better scoping'
                })
            
            if 'eval(' in stripped:
                results['bugs'].append({
                    'type': 'Security Bug',
                    'line': i,
                    'message': 'eval() is dangerous and should be avoided',
                    'suggestion': 'Remove eval() - it can execute arbitrary code and is a security risk'
                })
            
            if 'console.log' in stripped or 'console.error' in stripped:
                results['suggestions'].append({
                    'type': 'Production Code',
                    'line': i,
                    'message': 'Console statement found',
                    'suggestion': 'Remove console statements before deploying to production'
                })
            
            if 'undefined' in stripped.lower():
                results['warnings'].append({
                    'type': 'Undefined Check',
                    'line': i,
                    'message': 'Checking for undefined',
                    'suggestion': 'Consider using optional chaining (?.) or nullish coalescing (??)'
                })
            
            if stripped.count('function(') > 2 or stripped.count('=>') > 2:
                results['suggestions'].append({
                    'type': 'Code Quality',
                    'line': i,
                    'message': 'Multiple nested callbacks detected',
                    'suggestion': 'Consider using async/await or Promises to avoid callback hell'
                })
    
    def check_modern_practices(self, lines, results):
        """Check for modern JavaScript practices"""
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            
            if '+' in stripped and ('"' in stripped or "'" in stripped):
                if any(keyword in stripped for keyword in ['var ', 'let ', 'const ']):
                    results['suggestions'].append({
                        'type': 'Modern JS',
                        'line': i,
                        'message': 'String concatenation with +',
                        'suggestion': 'Use template literals (backticks) for string interpolation: `Hello ${name}`'
                    })
            
            if 'function(' in stripped and stripped.count('\n') == 0:
                if 'this' not in stripped:
                    results['suggestions'].append({
                        'type': 'Modern JS',
                        'line': i,
                        'message': 'Traditional function syntax',
                        'suggestion': 'Consider using arrow function syntax: () => { } for conciseness'
                    })
            
            if '.then(' in stripped:
                if '.catch(' not in ''.join(lines[i:min(i+5, len(lines))]):
                    results['warnings'].append({
                        'type': 'Error Handling',
                        'line': i,
                        'message': 'Promise without .catch()',
                        'suggestion': 'Always handle Promise rejections with .catch() or try/catch'
                    })
            
            if 'for (' in stripped and ('i = 0' in stripped or 'i < ' in stripped):
                results['suggestions'].append({
                    'type': 'Modern JS',
                    'line': i,
                    'message': 'Traditional for loop',
                    'suggestion': 'Consider using array methods like .forEach(), .map(), .filter() for cleaner code'
                })
