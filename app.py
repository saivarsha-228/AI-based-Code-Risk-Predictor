from flask import Flask, request, jsonify, send_from_directory
import lizard
import os

# Initialize Flask to serve files from the current directory
app = Flask(__name__, static_folder='.', template_folder='.')

@app.route('/')
def home():
    """Serves the main Ingestion/Analyzer page."""
    return send_from_directory('.', 'analyzer.html')

@app.route('/audit')
def audit_page():
    """Serves the separate results/report page."""
    return send_from_directory('.', 'audit.html')

@app.route('/main.js')
def serve_js():
    """Serves the JavaScript logic file."""
    return send_from_directory('.', 'main.js')

@app.route('/api/audit', methods=['POST'])
def run_polyglot_audit():
    """The Intelligence Engine: Analyzes complexity and vulnerability patterns."""
    data = request.json
    code_content = data.get('code', '')

    if not code_content:
        return jsonify({"status": "error", "message": "No code provided"}), 400

    try:
        # 1. Multi-Language Complexity Analysis (Lizard)
        # This works for C, C++, Java, JS, Python, PHP, Ruby, etc.
        analysis = lizard.analyze_file.analyze_source_code("input_stream.txt", code_content)
        
        # Calculate Average Cyclomatic Complexity
        if analysis.function_list:
            avg_complexity = sum(f.cyclomatic_complexity for f in analysis.function_list) / len(analysis.function_list)
        else:
            avg_complexity = 1  # Default for flat scripts

        # Assign Professional Grade
        grade = "A" if avg_complexity <= 5 else "B" if avg_complexity <= 12 else "C"

        # 2. Universal Vulnerability Pattern Detection
        # Searches for dangerous logic patterns across all programming languages
        threat_library = {
            'CRITICAL_INJECTION': ['eval(', 'exec(', 'system(', 'Popen(', 'shell=True'],
            'DATABASE_RISK': ['SELECT *', 'DROP TABLE', 'WHERE 1=1', 'INSERT INTO'],
            'SENSITIVE_EXPOSURE': ['password', 'secret_key', 'api_token', 'private_key', 'credentials'],
            'UNSAFE_PERMISSIONS': ['chmod 777', 'sudo ', 'allow_all']
        }

        detected_vectors = []
        for category, keywords in threat_library.items():
            if any(key.lower() in code_content.lower() for key in keywords):
                detected_vectors.append(category)

        # 3. Final Risk Probability (AI Simulation)
        risk_score = round(min((len(detected_vectors) * 0.22) + (avg_complexity * 0.03), 0.98), 2)

        return jsonify({
            "status": "success",
            "score": risk_score,
            "complexity": grade,
            "raw_complexity": round(avg_complexity, 1),
            "vector_count": len(detected_vectors),
            "details": detected_vectors,
            "engine": "Lizard Polyglot v4.0"
        })

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    # Running on port 5000 by default
    app.run(debug=True, port=5000)
