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

// =============================================================================
// Discord-Formatted Clipboard Functions
// =============================================================================

// Format a single pick for Discord (with markdown)
export function formatPickForDiscord(pick: {
  player_name: string;
  stat_type: string;
  line: number;
  side: string;
  odds?: number;
  model_probability?: number;
  expected_value?: number;
  team?: string;
}): string {
  const sideEmoji = pick.side === 'over' ? '⬆️' : '⬇️';
  const prob = pick.model_probability ? `${(pick.model_probability * 100).toFixed(0)}%` : '';
  const ev = pick.expected_value ? `+${(pick.expected_value * 100).toFixed(1)}% EV` : '';
  const odds = pick.odds ? `@ ${pick.odds > 0 ? '+' : ''}${pick.odds}` : '';
  
  let line = `**${pick.player_name}**`;
  if (pick.team) line += ` (${pick.team})`;
  line += `\n${sideEmoji} ${pick.side.toUpperCase()} ${pick.line} ${pick.stat_type}`;
  if (odds) line += ` ${odds}`;
  if (prob || ev) {
    line += `\n📊 ${prob}${prob && ev ? ' | ' : ''}${ev}`;
  }
  
  return line;
}

// Format multiple picks for Discord
export function formatPicksForDiscord(picks: Array<{
  player_name: string;
  stat_type: string;
  line: number;
  side: string;
  odds?: number;
  model_probability?: number;
  expected_value?: number;
  team?: string;
}>): string {
  const header = `🎯 **Perplex Engine Picks** - ${new Date().toLocaleDateString()}`;
  const divider = '━━━━━━━━━━━━━━━━━━━━';
  
  const pickLines = picks.map((p, i) => {
    const sideEmoji = p.side === 'over' ? '⬆️' : '⬇️';
    const ev = p.expected_value ? `+${(p.expected_value * 100).toFixed(1)}%` : '';
    return `**${i + 1}.** ${p.player_name} ${sideEmoji} ${p.side.toUpperCase()} ${p.line} ${p.stat_type}${ev ? ` (${ev})` : ''}`;
  });
  
  const footer = `\n🔗 *via Perplex Engine*`;
  
  return `${header}\n${divider}\n\n${pickLines.join('\n')}\n${footer}`;
}

// Format a parlay for Discord
export function formatParlayForDiscord(legs: Array<{
  player_name: string;
  stat_type: string;
  line: number;
  side: string;
}>, totalOdds: number, parlayEv: number): string {
  const header = `🎰 **Perplex Engine Parlay** - ${new Date().toLocaleDateString()}`;
  const divider = '━━━━━━━━━━━━━━━━━━━━';
  
  const legLines = legs.map((leg, i) => {
    const sideEmoji = leg.side === 'over' ? '⬆️' : '⬇️';
    return `**${i + 1}.** ${leg.player_name} ${sideEmoji} ${leg.side.toUpperCase()} ${leg.line} ${leg.stat_type}`;
  });
  
  const oddsStr = totalOdds > 0 ? `+${totalOdds}` : totalOdds.toString();
  const evStr = parlayEv >= 0 ? `+${(parlayEv * 100).toFixed(1)}%` : `${(parlayEv * 100).toFixed(1)}%`;
  const footer = `\n💰 **Odds:** ${oddsStr} | **EV:** ${evStr}\n🔗 *via Perplex Engine*`;
  
  return `${header}\n${divider}\n\n${legLines.join('\n')}\n${footer}`;
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
