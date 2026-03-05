from flask import Flask, request, jsonify, send_from_directory
import lizard
import os
import json
from datetime import datetime

from modules.smells import detect_code_smells
from modules.vulnerabilities import detect_vulnerabilities
from modules.risk import calculate_risk
from modules.report import generate_report
from modules.history import init_db, save_scan

app = Flask(__name__, static_folder='.', template_folder='.')

init_db()

@app.route('/')
def home():
    return send_from_directory('.', 'analyzer.html')

@app.route('/audit')
def audit_page():
    return send_from_directory('.', 'audit.html')

@app.route('/main.js')
def serve_js():
    return send_from_directory('.', 'main.js')


@app.route('/api/audit', methods=['POST'])
def run_polyglot_audit():

    data = request.json
    code_content = data.get('code', '')

    if not code_content:
        return jsonify({"status": "error", "message": "No code provided"}), 400

    try:

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

        vulnerabilities = detect_vulnerabilities(code_content)

        smells = detect_code_smells(code_content)

        risk_score, severity = calculate_risk(
            vulnerabilities,
            smells,
            avg_complexity
        )

        report = generate_report(
            risk_score,
            severity,
            round(avg_complexity,1),
            smells,
            vulnerabilities
        )

        save_scan(risk_score, severity, avg_complexity)

        report_data = {
            "risk_score": risk_score,
            "severity": severity,
            "complexity": avg_complexity,
            "vulnerabilities": vulnerabilities,
            "smells": smells,
            "report": report,
            "timestamp": datetime.now().strftime("%Y%m%d_%H%M%S")
        }

        os.makedirs("reports", exist_ok=True)

        json_file = f"reports/report_{report_data['timestamp']}.json"

        with open(json_file, "w") as f:
            json.dump(report_data, f, indent=4)

        return jsonify({
            "status": "success",
            "score": risk_score,
            "severity": severity,
            "complexity": grade,
            "raw_complexity": round(avg_complexity,1),
            "details": vulnerabilities,
            "smells": smells,
            "report": report,
            "json_report": json_file
        })

    except Exception as e:

        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
