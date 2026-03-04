document.addEventListener('DOMContentLoaded', () => {
    if (typeof lucide !== 'undefined') lucide.createIcons();
    
    // If the user is on the audit page, automatically trigger the analysis
    if (window.location.pathname.includes('/audit')) {
        loadAuditReport();
    }
});

/**
 * Page 1: analyzer.html Logic
 */
function startPolyAudit() {
    const codeArea = document.getElementById('codeIn'); // Matches the ID in analyzer.html
    if (!codeArea || !codeArea.value.trim()) {
        alert("Please paste some code first.");
        return;
    }

    // Save to browser memory to use on the next page
    localStorage.setItem('sentinel_pending_code', codeArea.value);
    
    // Visual feedback: Move to next step
    const steps = document.querySelectorAll('.step');
    if(steps[1]) steps[1].classList.add('active');

    // Redirect to the separate audit page
    setTimeout(() => {
        window.location.href = '/audit';
    }, 500);
}

/**
 * Page 2: audit.html Logic
 */
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
            // Populate the Report Page
            document.getElementById('grade').innerText = `Grade ${data.complexity}`;
            document.getElementById('v_count').innerText = data.vector_count;
            
            const gradeEl = document.getElementById('grade');
            gradeEl.style.color = data.complexity === 'A' ? '#3fb950' : '#f85149';

            const pBox = document.getElementById('patterns');
            if (pBox) {
                pBox.innerHTML = data.details.length > 0 
                    ? data.details.map(v => `<span class="tag danger">${v.replace('_', ' ')}</span>`).join('')
                    : '<span class="tag" style="color:#3fb950">INTEGRITY VERIFIED</span>';
            }
        }
    } catch (err) {
        console.error("Connection to Backend failed.");
    }
}
