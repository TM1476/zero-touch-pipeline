import re

class CAnalyzer:
    def __init__(self):
        self.name = "C Analyzer"
    
    def analyze(self, code):
        """Analyze C code for bugs and issues"""
        results = {
            'language': 'C',
            'bugs': [],
            'warnings': [],
            'suggestions': [],
            'score': 0
        }
        
        try:
            lines = code.split('\n')
            
            self.check_syntax(lines, results)
            
            self.check_memory_issues(lines, results)
            
            self.check_common_issues(lines, results)
            
            total_issues = len(results['bugs']) + len(results['warnings'])
            if total_issues == 0:
                results['score'] = 100
                results['suggestions'].append({
                    'type': 'success',
                    'message': 'No major issues found in C code',
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
        """Check for basic C syntax issues"""
        brace_count = 0
        paren_count = 0
        
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            
            if stripped.startswith('//') or stripped.startswith('/*') or not stripped:
                continue
            
            if any(keyword in stripped for keyword in ['int ', 'float ', 'char ', 'double ', 'return ']):
                if not stripped.endswith(';') and not stripped.endswith('{') and not stripped.endswith('}'):
                    if '(' not in stripped or ')' in stripped:
                        results['bugs'].append({
                            'type': 'Syntax Error',
                            'line': i,
                            'message': 'Missing semicolon at end of statement',
                            'suggestion': 'Add semicolon (;) at the end of the statement'
                        })
            
            brace_count += stripped.count('{') - stripped.count('}')
            paren_count += stripped.count('(') - stripped.count(')')
        
        if brace_count != 0:
            results['bugs'].append({
                'type': 'Syntax Error',
                'line': 0,
                'message': 'Unbalanced braces in code',
                'suggestion': f'Check your curly braces - {abs(brace_count)} brace(s) unmatched'
            })
        
        if paren_count != 0:
            results['bugs'].append({
                'type': 'Syntax Error',
                'line': 0,
                'message': 'Unbalanced parentheses in code',
                'suggestion': f'Check your parentheses - {abs(paren_count)} parenthesis unmatched'
            })
    
    def check_memory_issues(self, lines, results):
        """Check for potential memory management issues"""
        malloc_lines = []
        free_lines = []
        
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            
            if 'malloc(' in stripped or 'calloc(' in stripped:
                malloc_lines.append(i)
                
                if '=' not in stripped:
                    results['warnings'].append({
                        'type': 'Memory Warning',
                        'line': i,
                        'message': 'Memory allocation without assignment',
                        'suggestion': 'Assign malloc result to a pointer variable'
                    })
            
            if 'free(' in stripped:
                free_lines.append(i)
            
            if 'gets(' in stripped:
                results['bugs'].append({
                    'type': 'Security Bug',
                    'line': i,
                    'message': 'Dangerous function: gets() can cause buffer overflow',
                    'suggestion': 'Use fgets() instead of gets() for safe input'
                })
            
            if 'strcpy(' in stripped:
                results['warnings'].append({
                    'type': 'Security Warning',
                    'line': i,
                    'message': 'strcpy() can cause buffer overflow',
                    'suggestion': 'Consider using strncpy() or snprintf() for safer string operations'
                })
        
        if len(malloc_lines) > len(free_lines):
            results['warnings'].append({
                'type': 'Memory Leak Warning',
                'line': 0,
                'message': f'Potential memory leak: {len(malloc_lines)} malloc(s) but only {len(free_lines)} free(s)',
                'suggestion': 'Ensure every malloc/calloc has a corresponding free'
            })
    
    def check_common_issues(self, lines, results):
        """Check for common C programming issues"""
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            
            if 'if' in stripped and '=' in stripped and '==' not in stripped and '!=' not in stripped:
                if re.search(r'if\s*\([^)]*=[^=]', stripped):
                    results['warnings'].append({
                        'type': 'Logic Warning',
                        'line': i,
                        'message': 'Assignment (=) used in condition instead of comparison (==)',
                        'suggestion': 'Use == for comparison, = assigns a value'
                    })
            
            if any(keyword in stripped for keyword in ['int ', 'float ', 'char ', 'double ']):
                if ';' in stripped and '=' not in stripped:
                    results['warnings'].append({
                        'type': 'Initialization Warning',
                        'line': i,
                        'message': 'Variable declared but not initialized',
                        'suggestion': 'Initialize variables at declaration to avoid undefined behavior'
                    })
            
            if 'printf(' in stripped and '\\n' not in stripped:
                results['suggestions'].append({
                    'type': 'Style',
                    'line': i,
                    'message': 'printf without newline',
                    'suggestion': 'Consider adding \\n for better output formatting'
                })
