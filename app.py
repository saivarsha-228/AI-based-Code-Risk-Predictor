from flask import Flask, render_template, request, jsonify
import radon.complexity as cc
import ast
import joblib # To load your ML model

app = Flask(__name__)

# Mock ML Logic (Replace with joblib.load('model.pkl') later)
def predict_risk(code_text, complexity_score):
    # Professional Vector Detection
    danger_keywords = ['eval', 'exec', 'os.system', 'subprocess', 'SELECT', 'password']
    found_vectors = [word for word in danger_keywords if word in code_text.lower()]
    
    # Simple Weighting (Simulating Scikit-learn)
    # Risk increases with complexity and number of danger vectors
    base_risk = (len(found_vectors) * 0.2) + (complexity_score * 0.05)
    return min(round(base_risk, 2), 0.99), found_vectors

@app.route('/')
def dashboard():
    return render_template('index.html')

@app.route('/analyzer')
def analyzer_page():
    return render_template('analyzer.html')

@app.route('/api/audit', methods=['POST'])
def run_audit():
    data = request.json
    raw_code = data.get('code', '')

    try:
        # 1. Calculate Radon Complexity
        blocks = cc.cc_visit(raw_code)
        complexity_score = sum(b.complexity for b in blocks) if blocks else 1
        grade = "A" if complexity_score <= 5 else "B" if complexity_score <= 10 else "C"

        # 2. Run ML Prediction
        risk_score, vectors = predict_risk(raw_code, complexity_score)

        return jsonify({
            "status": "success",
            "score": risk_score,
            "complexity": grade,
            "vector_count": len(vectors),
            "details": vectors
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True, port=5000)
