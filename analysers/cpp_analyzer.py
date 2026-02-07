import re

class CppAnalyzer:
    def __init__(self):
        self.name = "C++ Analyzer"
    
    def analyze(self, code):
        """Analyze C++ code for bugs and issues"""
        results = {
            'language': 'C++',
            'bugs': [],
            'warnings': [],
            'suggestions': [],
            'score': 0
        }
        
        try:
            lines = code.split('\n')
            
            self.check_syntax(lines, results)
            
            self.check_memory_issues(lines, results)
            
            self.check_cpp_specific(lines, results)
            
            total_issues = len(results['bugs']) + len(results['warnings'])
            if total_issues == 0:
                results['score'] = 100
                results['suggestions'].append({
                    'type': 'success',
                    'message': 'No major issues found in C++ code',
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
        """Check for basic C++ syntax issues"""
        brace_count = 0
        has_main = False
        
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            
            if 'int main' in stripped or 'void main' in stripped:
                has_main = True
            
            if stripped.startswith('//') or stripped.startswith('/*') or not stripped:
                continue
            
            if any(keyword in stripped for keyword in ['int ', 'float ', 'string ', 'double ', 'return ', 'cout', 'cin']):
                if not stripped.endswith(';') and not stripped.endswith('{') and not stripped.endswith('}') and not stripped.endswith(':'):
                    if 'namespace' not in stripped and 'class' not in stripped:
                        results['bugs'].append({
                            'type': 'Syntax Error',
                            'line': i,
                            'message': 'Missing semicolon at end of statement',
                            'suggestion': 'Add semicolon (;) at the end of the statement'
                        })
            
            brace_count += stripped.count('{') - stripped.count('}')
        
        if brace_count != 0:
            results['bugs'].append({
                'type': 'Syntax Error',
                'line': 0,
                'message': 'Unbalanced braces in code',
                'suggestion': f'Check your curly braces - {abs(brace_count)} brace(s) unmatched'
            })
        
        if len(lines) > 10 and not has_main:
            results['warnings'].append({
                'type': 'Structure Warning',
                'line': 0,
                'message': 'No main() function found',
                'suggestion': 'Every C++ program needs an int main() function'
            })
    
    def check_memory_issues(self, lines, results):
        """Check for memory management issues"""
        new_count = 0
        delete_count = 0
        
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            
            if ' new ' in stripped:
                new_count += 1
                
                if '=' not in stripped:
                    results['warnings'].append({
                        'type': 'Memory Warning',
                        'line': i,
                        'message': 'Memory allocation without assignment',
                        'suggestion': 'Assign new operator result to a pointer'
                    })
            
            if 'delete ' in stripped:
                delete_count += 1
            
            if ' new[' in stripped:
                results['suggestions'].append({
                    'type': 'Memory',
                    'line': i,
                    'message': 'Array allocated with new[]',
                    'suggestion': 'Remember to use delete[] (not delete) to free this array'
                })
        
        if new_count > delete_count:
            results['warnings'].append({
                'type': 'Memory Leak Warning',
                'line': 0,
                'message': f'Potential memory leak: {new_count} new but only {delete_count} delete',
                'suggestion': 'Every new should have a corresponding delete. Consider using smart pointers.'
            })
    
    def check_cpp_specific(self, lines, results):
        """Check for C++ specific issues"""
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            
            if 'using namespace std' in stripped:
                results['suggestions'].append({
                    'type': 'Best Practice',
                    'line': i,
                    'message': 'using namespace std found',
                    'suggestion': 'Avoid "using namespace std" in header files. Use std:: prefix instead.'
                })
            
            if i == 1 and '#ifndef' not in stripped and '#pragma once' not in stripped:
                if '#include' in stripped or 'class' in stripped:
                    results['suggestions'].append({
                        'type': 'Best Practice',
                        'line': 1,
                        'message': 'Missing include guard',
                        'suggestion': 'Add #pragma once or #ifndef guards at the top of header files'
                    })
            
            if '*' in stripped and 'new' in stripped:
                results['suggestions'].append({
                    'type': 'Modern C++',
                    'line': i,
                    'message': 'Raw pointer with new',
                    'suggestion': 'Consider using smart pointers (unique_ptr, shared_ptr) instead of raw pointers'
                })
          
            if re.search(r'\([a-zA-Z_][a-zA-Z0-9_]*\s*\*?\)', stripped):
                if 'static_cast' not in stripped and 'dynamic_cast' not in stripped:
                    results['suggestions'].append({
                        'type': 'Modern C++',
                        'line': i,
                        'message': 'C-style cast detected',
                        'suggestion': 'Use C++ style casts: static_cast, dynamic_cast, const_cast, or reinterpret_cast'
                    })
