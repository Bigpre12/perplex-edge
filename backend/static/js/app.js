const API_BASE = window.location.origin;

document.addEventListener('DOMContentLoaded', () => {
    // Initial status check
    checkBackend();
    
    // Load endpoints if the container exists
    if (document.getElementById('endpoints-grid')) {
        loadEndpoints();
    }
});

async function checkBackend() {
    const statusBadge = document.getElementById('backend-status-badge');
    const statusText = document.getElementById('backend-status-text');
    
    if (!statusBadge) return;

    try {
        const response = await fetch(`${API_BASE}/health`);
        const data = await response.json();
        
        if (data.status === 'healthy') {
            updateStatus('healthy', 'Operational');
        } else {
            updateStatus('unhealthy', 'Issues Detected');
        }
    } catch (error) {
        updateStatus('unhealthy', 'Connection Failed');
        console.error('Backend check failed:', error);
    }
}

function updateStatus(state, text) {
    const badge = document.getElementById('backend-status-badge');
    const label = document.getElementById('backend-status-text');
    
    // Reset classes
    badge.className = 'status-badge';
    
    if (state === 'healthy') {
        badge.classList.add('status-healthy');
        badge.innerHTML = '✅ healthy';
    } else if (state === 'checking') {
        badge.classList.add('status-checking');
        badge.innerHTML = '🔄 checking...';
    } else {
        badge.classList.add('status-unhealthy');
        badge.innerHTML = '⚠️ unhealthy';
    }
    
    if (label) label.textContent = text;
}

function loadEndpoints() {
    const grid = document.getElementById('endpoints-grid');
    if (!grid) return;

    const endpoints = [
        { path: '/health', description: 'System health and status check', icon: '🩺' },
        { path: '/immediate/working-player-props', description: 'Real-time player prop analysis', icon: '⚡' },
        { path: '/immediate/brain-metrics', description: 'AI decision engine metrics', icon: '🧠' },
        { path: '/immediate/picks', description: 'Generated betting picks', icon: '🎯' },
        { path: '/track-record/track-record', description: 'Historical performance data', icon: '📊' },
        { path: '/status/model-status', description: 'ML model operational status', icon: '🤖' },
        { path: '/docs', description: 'Full API Documentation (Swagger)', icon: '📚' }
    ];

    grid.innerHTML = endpoints.map(ep => `
        <div class="endpoint-card" onclick="testEndpoint('${ep.path}')">
            <span class="endpoint-path">${ep.icon} ${ep.path}</span>
            <p class="endpoint-desc">${ep.description}</p>
            <button class="btn btn-secondary" style="width: 100%; justify-content: center; padding: 8px;">
                Test Endpoint
            </button>
        </div>
    `).join('');
}

async function testEndpoint(path) {
    // If it's docs, open in new tab
    if (path === '/docs') {
        window.open(`${API_BASE}/docs`, '_blank');
        return;
    }

    const btn = event.currentTarget.querySelector('button');
    const originalText = btn.innerText;
    btn.innerText = 'Testing...';
    
    try {
        const response = await fetch(`${API_BASE}${path}`);
        const data = await response.json();
        
        // Create a modal or nice alert to show results
        // For now, using a simple formatted alert, but in a real app would likely use a modal
        console.log(`Response from ${path}:`, data);
        alert(`Endpoint: ${path}\nStatus: ${response.status}\n\nResponse:\n${JSON.stringify(data, null, 2).substring(0, 500)}${JSON.stringify(data).length > 500 ? '...' : ''}`);
    } catch (error) {
        alert(`Error testing ${path}:\n${error.message}`);
    } finally {
        btn.innerText = originalText;
    }
}
