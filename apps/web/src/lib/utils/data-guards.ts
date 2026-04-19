/**
 * Coerce API payloads to a plain array (never null / object mistaken for list).
 */
export function toArray<T>(val: unknown): T[] {
  if (Array.isArray(val)) {
    return val as T[];
  }
  if (val == null) {
    return [];
  }
  if (typeof val === "object") {
    const o = val as Record<string, unknown>;
    for (const key of ["items", "data", "history", "results", "trends", "records"] as const) {
      const inner = o[key];
      if (Array.isArray(inner)) {
        return inner as T[];
      }
    }
  }
  return [];
}
