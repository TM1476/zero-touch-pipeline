import re

class JavaAnalyzer:
    def __init__(self):
        self.name = "Java Analyzer"
    
    def analyze(self, code):
        """Analyze Java code for bugs and issues"""
        results = {
            'language': 'Java',
            'bugs': [],
            'warnings': [],
            'suggestions': [],
            'score': 0
        }
        
        try:
            lines = code.split('\n')
            
            self.check_syntax(lines, results)
            
            self.check_common_issues(lines, results)
            
            self.check_best_practices(lines, results)

            total_issues = len(results['bugs']) + len(results['warnings'])
            if total_issues == 0:
                results['score'] = 100
                results['suggestions'].append({
                    'type': 'success',
                    'message': 'No major issues found in Java code',
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
        """Check for basic Java syntax issues"""
        brace_count = 0
        has_class = False
        has_main = False
        
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            
            if 'class ' in stripped:
                has_class = True
                match = re.search(r'class\s+([A-Za-z_][A-Za-z0-9_]*)', stripped)
                if match:
                    class_name = match.group(1)
                    if not class_name[0].isupper():
                        results['warnings'].append({
                            'type': 'Naming Convention',
                            'line': i,
                            'message': f'Class name "{class_name}" should start with uppercase',
                            'suggestion': 'Java classes should follow PascalCase naming (e.g., MyClass)'
                        })
            
            if 'public static void main' in stripped:
                has_main = True
            
            if stripped.startswith('//') or stripped.startswith('/*') or not stripped:
                continue
            
            if any(keyword in stripped for keyword in ['int ', 'String ', 'boolean ', 'return ', 'System.out']):
                if not stripped.endswith(';') and not stripped.endswith('{') and not stripped.endswith('}'):
                    if 'class' not in stripped and 'public' not in stripped and 'private' not in stripped:
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
        
        if len(lines) > 5 and not has_class:
            results['bugs'].append({
                'type': 'Structure Error',
                'line': 0,
                'message': 'No class definition found',
                'suggestion': 'Java code must be inside a class'
            })
    
    def check_common_issues(self, lines, results):
        """Check for common Java programming issues"""
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            
            if 'String' in stripped or '"' in stripped:
                if ' == ' in stripped or ' != ' in stripped:
                    if '"' in stripped:
                        results['bugs'].append({
                            'type': 'Logic Bug',
                            'line': i,
                            'message': 'Using == to compare Strings',
                            'suggestion': 'Use .equals() method to compare String values, not =='
                        })
            
            if '.' in stripped and 'null' in stripped.lower():
                results['warnings'].append({
                    'type': 'Null Safety',
                    'line': i,
                    'message': 'Potential NullPointerException',
                    'suggestion': 'Check for null before calling methods on objects'
                })
            
            if 'catch' in stripped:
                if i < len(lines):
                    next_few = ''.join(lines[i:min(i+3, len(lines))])
                    if '{}' in next_few or ('catch' in stripped and '{' in next_few and '}' in next_few and next_few.count('\n') < 2):
                        results['warnings'].append({
                            'type': 'Error Handling',
                            'line': i,
                            'message': 'Empty or minimal catch block',
                            'suggestion': 'Avoid empty catch blocks. At minimum, log the exception.'
                        })
            
            if 'System.out.print' in stripped:
                results['suggestions'].append({
                    'type': 'Best Practice',
                    'line': i,
                    'message': 'System.out.print found',
                    'suggestion': 'Use a logging framework instead of System.out for production code'
                })
    
    def check_best_practices(self, lines, results):
        """Check for Java best practices"""
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            
            if any(keyword in stripped for keyword in ['int ', 'String ', 'boolean ', 'double ', 'float ']):
                match = re.search(r'(int|String|boolean|double|float)\s+([A-Za-z_][A-Za-z0-9_]*)', stripped)
                if match:
                    var_name = match.group(2)
                    if var_name[0].isupper() and 'final' not in stripped:
                        results['warnings'].append({
                            'type': 'Naming Convention',
                            'line': i,
                            'message': f'Variable "{var_name}" should start with lowercase',
                            'suggestion': 'Java variables should follow camelCase naming (e.g., myVariable)'
                        })
            
            if 'public ' in stripped and '(' in stripped and ')' in stripped:
                if any(method in stripped for method in ['toString', 'equals', 'hashCode']):
                    if i > 1 and '@Override' not in lines[i-2]:
                        results['suggestions'].append({
                            'type': 'Best Practice',
                            'line': i,
                            'message': 'Override method without @Override annotation',
                            'suggestion': 'Add @Override annotation when overriding methods'
                        })
            
            if 'ArrayList' in stripped or 'HashMap' in stripped or 'List' in stripped:
                if '<' not in stripped or '>' not in stripped:
                    results['warnings'].append({
                        'type': 'Type Safety',
                        'line': i,
                        'message': 'Raw type usage detected',
                        'suggestion': 'Use generics for type safety (e.g., ArrayList<String>)'
                    })
