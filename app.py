from flask import Flask, request, jsonify, send_from_directory
import lizard
import os

app = Flask(__name__, static_folder='.', template_folder='.')

@app.route('/')
def home():
    return send_from_directory('.', 'analyzer.html')

@app.route('/audit')
def audit_page():
    return send_from_directory('.', 'audit.html')

@app.route('/main.js')
def serve_js():
    return send_from_directory('.', 'main.js')


# -------------------------
# CODE SMELL DETECTION
# -------------------------
def detect_code_smells(code):

    smells = []

    if len(code.splitlines()) > 250:
        smells.append("Large File Size")

    if code.count("if(") + code.count("if (") > 10:
        smells.append("Too Many Conditional Branches")

    if code.count("for(") + code.count("while(") > 8:
        smells.append("Excessive Looping")

    if "global " in code:
        smells.append("Global Variable Usage")

    if "goto " in code:
        smells.append("Use of GOTO Statement")

    return smells


# -------------------------
# VULNERABILITY DETECTION
# -------------------------
def detect_vulnerabilities(code):

    threat_library = {
        'INJECTION_VECTOR': ['eval(', 'exec(', 'system(', 'SELECT *', 'DROP TABLE'],
        'SENSITIVE_DATA': ['password', 'secret_key', 'api_token'],
        'PERMISSION_RISK': ['chmod 777', 'sudo ']
    }

    detected = []

    for category, keys in threat_library.items():
        for key in keys:
            if key.lower() in code.lower():
                detected.append(category)
                break

    return detected


# -------------------------
# SEVERITY LEVEL
# -------------------------
def calculate_severity(score):

    if score < 0.30:
        return "LOW"
    elif score < 0.60:
        return "MEDIUM"
    else:
        return "HIGH"


# -------------------------
# REPORT GENERATION
# -------------------------
def generate_report(score, severity, complexity, smells, vulnerabilities):

    report = f"""
CODE SECURITY ANALYSIS REPORT
----------------------------------

Risk Score : {score}
Severity   : {severity}
Complexity : {complexity}

Detected Vulnerabilities:
{', '.join(vulnerabilities) if vulnerabilities else 'None'}

Code Smells:
{', '.join(smells) if smells else 'None'}

Recommendation:
Review high complexity functions and remove risky patterns such as eval() or hardcoded secrets.
"""

    return report.strip()


# -------------------------
# MAIN ANALYSIS API
# -------------------------
@app.route('/api/audit', methods=['POST'])
def run_polyglot_audit():

    data = request.json
    code_content = data.get('code', '')

    if not code_content:
        return jsonify({"status": "error", "message": "No code provided"}), 400

    try:

        # COMPLEXITY ANALYSIS
        analysis = lizard.analyze_file.analyze_source_code(
            "input_stream.txt", code_content
        )

        if analysis.function_list:
            avg_complexity = sum(
                f.cyclomatic_complexity for f in analysis.function_list
            ) / len(analysis.function_list)
        else:
            avg_complexity = 1

        grade = "A" if avg_complexity <= 5 else "B" if avg_complexity <= 12 else "C"


        # DETECTIONS
        vulnerabilities = detect_vulnerabilities(code_content)
        smells = detect_code_smells(code_content)


        # RISK SCORE
        risk_score = round(
            min(
                (len(vulnerabilities) * 0.25) +
                (len(smells) * 0.15) +
                (avg_complexity * 0.03),
                0.99
            ),
            2
        )


        severity = calculate_severity(risk_score)


        report = generate_report(
            risk_score,
            severity,
            round(avg_complexity, 1),
            smells,
            vulnerabilities
        )


        return jsonify({
            "status": "success",

            "score": risk_score,
            "severity": severity,

            "complexity": grade,
            "raw_complexity": round(avg_complexity, 1),

            "vector_count": len(vulnerabilities),
            "details": vulnerabilities,

            "smells": smells,
            "report": report
        })


    except Exception as e:

        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
