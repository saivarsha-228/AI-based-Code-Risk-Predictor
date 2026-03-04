async function performAudit() {
    const code = document.getElementById('codeEditor').value;
    const log = document.getElementById('consoleLogs');
    
    log.innerHTML = "[SENTINEL] Connecting to Python Kernel...\n";

    const response = await fetch('/api/audit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code: code })
    });
    
    const data = await response.json();
    
    // Update the UI
    document.getElementById('riskValue').innerText = data.score;
    document.getElementById('compGrade').innerText = data.complexity;
    document.getElementById('vectorCount').innerText = data.vector_count;
    
    log.innerHTML += "[SUCCESS] Analysis synced with Python Backend.\n";
}
