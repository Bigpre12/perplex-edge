/**
 * Robust date parsing for the LUCRX frontend.
 * Handles various ISO formats and potential null values.
 */
export function safeDate(dateStr: string | Date | null | undefined): Date | null {
    if (!dateStr) return null;
    if (dateStr instanceof Date) return isNaN(dateStr.getTime()) ? null : dateStr;
    
    try {
        // Ensure ISO format compatibility (replacing space with T if needed)
        const normalized = typeof dateStr === 'string' 
            ? dateStr.trim().replace(' ', 'T')
            : dateStr;
            
        const date = new Date(normalized);
        return isNaN(date.getTime()) ? null : date;
    } catch (e) {
        console.error("Failed to parse date:", dateStr, e);
        return null;
    }
}

/**
 * Formats a date into a clean HH:MM string.
 */
export function formatTime(date: Date | string | null | undefined): string {
    const d = safeDate(date);
    if (!d) return "--:--";
    return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}
