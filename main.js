
document.addEventListener('DOMContentLoaded', () => {
    if (typeof lucide !== 'undefined') lucide.createIcons();
    
    // Auto-run loadAuditReport if we are on the audit page
    if (window.location.pathname.includes('/audit')) {
        loadAuditReport();
    }
});

function startPolyAudit() {
    const codeArea = document.getElementById('polyCode');
    if (!codeArea || !codeArea.value.trim()) return alert("Buffer empty.");

    // Store in localStorage for cross-page persistence
    localStorage.setItem('sentinel_pending_code', codeArea.value);
    window.location.href = '/audit';
}

async function loadAuditReport() {
    const code = localStorage.getItem('sentinel_pending_code');
    if (!code) {
        window.location.href = '/';
        return;
    }

    try {
        const response = await fetch('/api/audit', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ code: code })
        });

        const data = await response.json();

        if (data.status === "success") {
            document.getElementById('grade').innerText = `Grade ${data.complexity}`;
            document.getElementById('v_count').innerText = data.vector_count;
            
            const gradeEl = document.getElementById('grade');
            gradeEl.style.color = data.complexity === 'A' ? '#3fb950' : '#f85149';

            const pBox = document.getElementById('patterns');
            pBox.innerHTML = data.details.length > 0 
                ? data.details.map(v => `<span class="tag danger">${v.replace('_', ' ')}</span>`).join('')
                : '<span class="tag" style="color:#3fb950">INTEGRITY VERIFIED</span>';
        }
    } catch (err) {
        console.error("Audit Pipeline Error:", err);
    }
}
