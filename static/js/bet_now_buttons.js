/**
 * static/js/bet_now_buttons.js
 * Professional deep-link buttons and hit rate components like Props.cash.
 */

function renderHitRateVsOdds(actualHitRate, impliedProb, edge) {
    const edgeColor = edge >= 0 ? '#00ff00' : '#ff4444';
    return `
        <div class="hit-rate-container" style="background: #1a1a1a; padding: 10px; border-radius: 8px; margin-top: 10px; border: 1px solid #333;">
            <div style="display: flex; justify-content: space-between; font-size: 0.85rem; margin-bottom: 5px;">
                <span style="color: #aaa;">L30 Hit Rate</span>
                <span style="color: #fff; font-weight: bold;">${actualHitRate}%</span>
            </div>
            <div style="display: flex; justify-content: space-between; font-size: 0.85rem; margin-bottom: 5px;">
                <span style="color: #aaa;">Implied Prob</span>
                <span style="color: #fff;">${impliedProb}%</span>
            </div>
            <div style="border-top: 1px solid #333; margin: 5px 0; padding-top: 5px; display: flex; justify-content: space-between; font-weight: bold;">
                <span style="color: #fff;">EDGE</span>
                <span style="color: ${edgeColor};">${edge > 0 ? '+' : ''}${edge}%</span>
            </div>
        </div>
    `;
}

function createBetNowButton(sportsbook, deepLink, player, ev) {
    const btn = document.createElement('button');
    btn.className = `btn-bet-${sportsbook.toLowerCase()}`;
    btn.innerHTML = `Bet on ${sportsbook}`;
    btn.style = "width: 100%; padding: 12px; margin-top: 8px; border-radius: 6px; border: none; font-weight: bold; cursor: pointer; background: #00ff00; color: #000;";

    btn.onclick = async () => {
        // Track the click for affiliate revenue
        try {
            await fetch('/api/affiliate/click', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ sportsbook, player, ev })
            });
        } catch (e) { console.error('Tracking failed', e); }

        window.open(deepLink, '_blank');
    };

    return btn;
}

// Export for use in app.js
window.LucrixUI = { renderHitRateVsOdds, createBetNowButton };
