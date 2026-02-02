/**
 * Clipboard utilities for copying betting picks and parlays
 */

// Format a single pick for clipboard
export function formatPickForClipboard(pick: {
  player_name: string;
  stat_type: string;
  line: number;
  side: string;
  odds?: number;
  model_probability?: number;
  expected_value?: number;
}): string {
  const oddsStr = pick.odds ? ` @ ${pick.odds > 0 ? '+' : ''}${pick.odds}` : '';
  const evStr = pick.expected_value ? ` (${(pick.expected_value * 100).toFixed(1)}% EV)` : '';
  return `${pick.player_name} ${pick.side.toUpperCase()} ${pick.line} ${pick.stat_type}${oddsStr}${evStr}`;
}

// Format multiple picks for clipboard (one per line)
export function formatPicksForClipboard(picks: Array<{
  player_name: string;
  stat_type: string;
  line: number;
  side: string;
  odds?: number;
  model_probability?: number;
  expected_value?: number;
}>): string {
  const header = `🎯 Perplex Engine Picks (${new Date().toLocaleDateString()})`;
  const lines = picks.map((p, i) => `${i + 1}. ${formatPickForClipboard(p)}`);
  return `${header}\n\n${lines.join('\n')}`;
}

// Format a parlay for clipboard
export function formatParlayForClipboard(legs: Array<{
  player_name: string;
  stat_type: string;
  line: number;
  side: string;
}>, totalOdds: number, parlayEv: number): string {
  const header = `🎰 Perplex Engine Parlay (${new Date().toLocaleDateString()})`;
  const legLines = legs.map((leg, i) => 
    `${i + 1}. ${leg.player_name} ${leg.side.toUpperCase()} ${leg.line} ${leg.stat_type}`
  );
  const footer = `\nTotal Odds: ${totalOdds > 0 ? '+' : ''}${totalOdds} | EV: ${(parlayEv * 100).toFixed(1)}%`;
  return `${header}\n\n${legLines.join('\n')}${footer}`;
}

// Copy text to clipboard and return success status
export async function copyToClipboard(text: string): Promise<boolean> {
  try {
    await navigator.clipboard.writeText(text);
    return true;
  } catch (err) {
    console.error('Failed to copy to clipboard:', err);
    // Fallback for older browsers
    try {
      const textarea = document.createElement('textarea');
      textarea.value = text;
      textarea.style.position = 'fixed';
      textarea.style.opacity = '0';
      document.body.appendChild(textarea);
      textarea.select();
      document.execCommand('copy');
      document.body.removeChild(textarea);
      return true;
    } catch (fallbackErr) {
      console.error('Fallback clipboard copy failed:', fallbackErr);
      return false;
    }
  }
}

// Toast notification state (can be used with a simple hook)
export interface ToastState {
  message: string;
  type: 'success' | 'error';
  visible: boolean;
}

// Simple hook for copy-to-clipboard with toast
export function useCopyToClipboard() {
  const copy = async (text: string, successMessage = 'Copied to clipboard!') => {
    const success = await copyToClipboard(text);
    return { success, message: success ? successMessage : 'Failed to copy' };
  };
  
  return { copy };
}
