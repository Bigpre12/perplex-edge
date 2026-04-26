export type Envelope<T> =
  | T[]
  | {
      data?: T[];
      results?: T[];
      items?: T[];
      props?: T[];
      edges?: T[];
      games?: T[];
    };

export function unwrapList<T>(payload: Envelope<T> | null | undefined): T[] {
  if (!payload) return [];
  if (Array.isArray(payload)) return payload;
  return payload.data || payload.results || payload.items || payload.props || payload.edges || payload.games || [];
}

