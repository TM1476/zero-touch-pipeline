const languageDropdown = document.getElementById('language');
const codeInput = document.getElementById('codeInput');
const analyzeBtn = document.getElementById('analyzeBtn');
const clearBtn = document.getElementById('clearBtn');
const resultsContainer = document.getElementById('resultsContainer');
const loadingOverlay = document.getElementById('loadingOverlay');
const lineCount = document.getElementById('lineCount');
const qualityScore = document.getElementById('qualityScore');
const scoreValue = document.getElementById('scoreValue');

codeInput.addEventListener('input', () => {
    const lines = codeInput.value.split('\n').length;
    lineCount.textContent = lines;
});

clearBtn.addEventListener('click', () => {
    codeInput.value = '';
    lineCount.textContent = '0';
    resultsContainer.innerHTML = `
        <div class="empty-state">
            <i class="fas fa-code"></i>
            <p>No analysis yet</p>
            <span>Paste your code and click "Analyze Code" to get started</span>
        </div>
    `;
    qualityScore.classList.add('hidden');
});

analyzeBtn.addEventListener('click', analyzeCode);

codeInput.addEventListener('keydown', (e) => {
    if (e.ctrlKey && e.key === 'Enter') {
        analyzeCode();
    }
});

document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

async function analyzeCode() {
    const code = codeInput.value.trim();
    const language = languageDropdown.value;
    
    if (!code) {
        showError('Please enter some code to analyze');
        return;
    }
    
    showLoading(true);
    
    try {
        const response = await fetch('/api/analyze', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                code: code,
                language: language
            })
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Analysis failed');
        }
        
        const results = await response.json();
        
        displayResults(results);
        
    } catch (error) {
        console.error('Analysis error:', error);
        showError(error.message || 'An error occurred during analysis');
    } finally {
        showLoading(false);
    }
}

function displayResults(results) {
    const score = results.score || 0;
    scoreValue.textContent = score;
    qualityScore.classList.remove('hidden');
    
    qualityScore.classList.remove('low', 'medium');
    if (score < 50) {
        qualityScore.classList.add('low');
    } else if (score < 80) {
        qualityScore.classList.add('medium');
    }
    
    let resultsHTML = '';
    
    const hasBugs = results.bugs && results.bugs.length > 0;
    const hasWarnings = results.warnings && results.warnings.length > 0;
    const hasSuggestions = results.suggestions && results.suggestions.length > 0;
    
    if (!hasBugs && !hasWarnings && !hasSuggestions) {
        resultsHTML = `
            <div class="empty-state">
                <i class="fas fa-check-circle" style="color: var(--success-color);"></i>
                <p>Great job!</p>
                <span>No issues found in your code. Quality Score: ${score}/100</span>
            </div>
        `;
    } else {
        if (hasBugs) {
            resultsHTML += createIssueSection('Bugs', results.bugs, 'bug', 'fas fa-bug', 'error-color');
        }
        
        if (hasWarnings) {
            resultsHTML += createIssueSection('Warnings', results.warnings, 'warning', 'fas fa-exclamation-triangle', 'warning-color');
        }
        
        if (hasSuggestions) {
            resultsHTML += createIssueSection('Suggestions', results.suggestions, 'suggestion', 'fas fa-lightbulb', 'success-color');
        }
    }
    
    resultsContainer.innerHTML = resultsHTML;
    
    resultsContainer.scrollTop = 0;
}

function createIssueSection(title, issues, type, icon, color) {
    let html = `
        <div class="issue-category">
            <div class="category-header">
                <i class="${icon}" style="color: var(--${color});"></i>
                <span>${title} (${issues.length})</span>
            </div>
    `;
    
    issues.forEach(issue => {
        html += createIssueCard(issue, type);
    });
    
    html += '</div>';
    return html;
}

function createIssueCard(issue, type) {
    const lineInfo = issue.line ? `Line ${issue.line}` : 'General';
    const message = issue.message || 'No message provided';
    const suggestion = issue.suggestion || 'No suggestion available';
    
    return `
        <div class="issue-card ${type}">
            <div class="issue-header">
                <span class="issue-type">${issue.type || type.charAt(0).toUpperCase() + type.slice(1)}</span>
                <span class="issue-line">${lineInfo}</span>
            </div>
            <div class="issue-message">${escapeHtml(message)}</div>
            <div class="issue-suggestion">
                <strong>💡 Suggestion:</strong> ${escapeHtml(suggestion)}
            </div>
        </div>
    `;
}

function showLoading(show) {
    if (show) {
        loadingOverlay.classList.remove('hidden');
    } else {
        loadingOverlay.classList.add('hidden');
    }
}

function showError(message) {
    resultsContainer.innerHTML = `
        <div class="empty-state">
            <i class="fas fa-exclamation-circle" style="color: var(--error-color);"></i>
            <p>Error</p>
            <span>${escapeHtml(message)}</span>
        </div>
    `;
    qualityScore.classList.add('hidden');
}

function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, m => map[m]);
}

const sampleCode = {
    python: `# Sample Python code with issues
def calculate_average(numbers):
    total = 0
    for num in numbers:
        total = total + num
    average = total / len(numbers)
    print(average)
    return average

# Call the function
result = calculate_average([1, 2, 3, 4, 5])`,

    c: `// Sample C code with issues
#include <stdio.h>

int main() {
    int x = 10;
    int y = 0;
    int result;
    
    result = x / y;  // Division by zero
    printf("Result: %d", result);
    
    return 0;
}`,

    cpp: `// Sample C++ code with issues
#include <iostream>
using namespace std;

int main() {
    int* ptr = new int(10);
    cout << *ptr << endl;
    // Memory leak - no delete
    
    int arr[5];
    arr[10] = 100;  // Array out of bounds
    
    return 0;
}`,

    java: `// Sample Java code with issues
public class Example {
    public static void main(String[] args) {
        String str1 = "Hello";
        String str2 = "Hello";
        
        if (str1 == str2) {  // Wrong string comparison
            System.out.println("Equal");
        }
        
        ArrayList list = new ArrayList();  // Raw type
        list.add("Item");
    }
}`,

    javascript: `// Sample JavaScript code with issues
function processData(data) {
    var result = [];
    
    for (var i = 0; i < data.length; i++) {
        result.push(data[i] * 2);
    }
    
    if (data == null) {  // Should use ===
        console.log("No data");
    }
    
    return result;
}

processData([1, 2, 3, 4, 5]);`
};

languageDropdown.addEventListener('change', () => {
    const selectedLanguage = languageDropdown.value;
    if (codeInput.value.trim() === '') {
        codeInput.value = sampleCode[selectedLanguage] || '';
        const lines = codeInput.value.split('\n').length;
        lineCount.textContent = lines;
    }
});

document.addEventListener('DOMContentLoaded', () => {
    console.log('Zero-Touch Code Analyzer initialized');
    
    lineCount.textContent = '0';
    
    const initialLanguage = languageDropdown.value;
    if (sampleCode[initialLanguage]) {
        codeInput.placeholder = `Paste your ${initialLanguage.toUpperCase()} code here or use the sample below...\n\n` + 
                                sampleCode[initialLanguage];
    }
});

document.addEventListener('keydown', (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        codeInput.focus();
    }
});

function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        console.log('Copied to clipboard');
    }).catch(err => {
        console.error('Failed to copy:', err);
    });
}

function exportResults(results) {
    const dataStr = JSON.stringify(results, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = 'code-analysis-results.json';
    link.click();
    URL.revokeObjectURL(url);
}

function trackEvent(eventName, eventData) {
    console.log(`Event: ${eventName}`, eventData);
}

function trackAnalysis(language, linesOfCode) {
    trackEvent('code_analyzed', {
        language: language,
        lines_of_code: linesOfCode,
        timestamp: new Date().toISOString()
    });
}
